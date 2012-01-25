#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import json

from voodoo.sessions.session_id import SessionId

from weblab.data.experiments import ExperimentId
import weblab.data.client_address as ClientAddress

import weblab.comm.web_server as WebFacadeServer
from weblab.core.coordinator.clients.ilab_batch import RequestSerializer

class ILabMethod(WebFacadeServer.Method):
    path = '/ilab/'

    def __init__(self, *args, **kwargs):
        super(ILabMethod, self).__init__(*args, **kwargs)
        self.other_cookies = []

    def run(self):
        self.serializer = RequestSerializer()
        action = self.req.headers.get('SOAPAction')
        if action is None:
            return "No SOAPAction provided"

        cookies = self.req.headers.getheader('cookie')

        self.sess_id = None
        self.reservation_id = None
        for cur_cookie in (cookies or '').split('; '):
            if cur_cookie.startswith("weblabsessionid="):
                self.sess_id = SessionId('.'.join(cur_cookie[len('weblabsessionid='):].split('.')[:-1]))
            if cur_cookie.startswith('weblab_reservation_id='):
                self.reservation_id = SessionId(cur_cookie[len('weblab_reservation_id='):].split('.')[0])

        if self.sess_id is None:
            return "Not logged in!"

        length = int(self.req.headers.getheader('content-length'))
        self.payload = self.req.rfile.read(length)

        methods = {
            '"http://ilab.mit.edu/GetLabConfiguration"'      : self.process_GetLabConfiguration,
            '"http://ilab.mit.edu/Submit"'                   : self.process_Submit,
            '"http://ilab.mit.edu/GetExperimentStatus"'      : self.process_GetExperimentStatus,
            '"http://ilab.mit.edu/RetrieveResult"'           : self.process_RetrieveResult,
            '"http://ilab.mit.edu/SaveAnnotation"'           : self.process_SaveAnnotation,
            '"http://ilab.mit.edu/ListAllClientItems"'       : self.process_ListAllClientItems,
            '"http://ilab.mit.edu/LoadClientItem"'           : self.process_LoadClientItem,
            '"http://ilab.mit.edu/SaveClientItem"'           : self.process_SaveClientItem,
            '"http://ilab.mit.edu/GetExperimentInformation"' : self.process_GetExperimentInformation,
        }

        if not action in methods:
            return "Action not found"

        return methods[action]()

    def get_content_type(self):
        return "text/xml"

    def get_other_cookies(self):
        return self.other_cookies

    def process_GetLabConfiguration(self):
        lab_server_id = self.serializer.parse_get_lab_configuration_request(self.payload)
        request = {
            'operation' : 'get_lab_configuration',
        }
        # TODO: client address
        reservation_status = self.server.reserve_experiment(self.sess_id, ExperimentId(lab_server_id, 'iLab experiments'), json.dumps(request), '{}', ClientAddress.ClientAddress(''))
        lab_configuration = reservation_status.initial_data
        return self.serializer.generate_lab_configuration_response(lab_configuration)

    def process_Submit(self):
        lab_server_id, experiment_specification, _, _ = self.serializer.parse_submit_request(self.payload)
        request = {
            'operation' : 'submit',
            'payload'   : experiment_specification
        }
        reservation_status = self.server.reserve_experiment(self.sess_id, ExperimentId(lab_server_id, 'iLab experiments'), json.dumps(request), '{}', ClientAddress.ClientAddress(''))
        self.other_cookies = ['weblab_reservation_id=%s; path=/' % reservation_status.reservation_id.id]

        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<SubmitResponse xmlns="http://ilab.mit.edu">
<SubmitResult>
<vReport>
<accepted>true</accepted>
<errorMessage />
<estRuntime>8</estRuntime>
</vReport>
<experimentID>61</experimentID>
<minTimeToLive>0</minTimeToLive>
<wait>
<effectiveQueueLength>%s</effectiveQueueLength>
<estWait>5</estWait>
</wait>
</SubmitResult>
</SubmitResponse>
</soap:Body>
</soap:Envelope>""" % reservation_status.position

    def process_GetExperimentStatus(self):
        if self.reservation_id is None:
            return "Reservation id not found in cookie"
        reservation_status = self.server.get_reservation_status(self.reservation_id)
        if reservation_status.status == "Reservation::waiting":
            length = reservation_status.position
            status = 1
        elif reservation_status.status == "Reservation::waiting_confirmation":
            length = 0
            status = 2
        elif reservation_status.status == "Reservation::post_reservation":
            length = 0
            status = 3
        else:
            raise Exception("Unexpected status in get_experimen_status: %s" % reservation_status.status) 

        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<GetExperimentStatusResponse xmlns="http://ilab.mit.edu">
<GetExperimentStatusResult>
<statusReport>
<statusCode>%s</statusCode>
<wait>
<effectiveQueueLength>%s</effectiveQueueLength>
<estWait>0</estWait>
</wait>
<estRuntime>0</estRuntime>
<estRemainingRuntime>0</estRemainingRuntime>
</statusReport>
<minTimetoLive>0</minTimetoLive>
</GetExperimentStatusResult>
</GetExperimentStatusResponse>
</soap:Body>
</soap:Envelope>""" % (status, length)

    def process_RetrieveResult(self):
        reservation_status = self.server.get_reservation_status(self.reservation_id)
        try:
            response = json.loads(reservation_status.initial_data)
        except:
            return "Error occurred: %s" % reservation_status.initial_data

        code       = response['code']
        results    = response['results']
        xmlResults = response['xmlResults']

        return self.serializer.generate_retrieve_result_response(code, results, xmlResults)

    ###############################################################
    # 
    # Methods not implemented in WebLab-Deusto
    # 
    def process_GetExperimentInformation(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetExperimentInformationResponse xmlns="http://ilab.mit.edu">
      <GetExperimentInformationResult>
        <ExperimentInformation>
          <experimentID>61</experimentID>
          <labServerID>15</labServerID>
          <userID>5</userID>
          <effectiveGroupID>5</effectiveGroupID>
          <submissionTime>2007-09-27T12:00:00Z</submissionTime>
          <completionTime>2007-09-27T12:00:00Z</completionTime>
          <expirationTime>2007-09-27T12:00:00Z</expirationTime>
          <minTimeToLive>5.0</minTimeToLive>
          <priorityHint>5</priorityHint>
          <statusCode>3</statusCode>
          <validationWarningMessages/>
          <validationErrorMessage>string</validationErrorMessage>
          <executionWarningMessages/>
          <executionErrorMessage/>
          <annotation/>
          <xmlResultExtension/>
          <xmlBlobExtension/>
        </ExperimentInformation>
      </GetExperimentInformationResult>
    </GetExperimentInformationResponse>
  </soap:Body>
</soap:Envelope>"""

    def process_SaveAnnotation(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<SaveAnnotationResponse xmlns="http://ilab.mit.edu">
<SaveAnnotationResult />
</SaveAnnotationResponse>
</soap:Body>
</soap:Envelope>"""

    def process_ListAllClientItems(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<ListAllClientItemsResponse xmlns="http://ilab.mit.edu">
<ListAllClientItemsResult>
</ListAllClientItemsResult>
</ListAllClientItemsResponse>
</soap:Body>
</soap:Envelope>"""

    def process_SaveClientItem(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <SaveClientItemResponse xmlns="http://ilab.mit.edu" />
  </soap:Body>
</soap:Envelope>"""

    def process_LoadClientItem(self):
        return "load client item"

