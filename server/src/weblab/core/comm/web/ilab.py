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

from weblab.core.exc import SessionNotFoundException
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
                self.sess_id = SessId(cur_cookie[len('weblabsessionid='):].split('.')[0])
            if cur_cookie.startswith('weblab_reservation_id='):
                self.reservation_id = cur_cookie[len('weblab_reservation_id='):].split('.')[0]

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
<effectiveQueueLength>0</effectiveQueueLength>
<estWait>5</estWait>
</wait>
</SubmitResult>
</SubmitResponse>
</soap:Body>
</soap:Envelope>"""

    def process_GetExperimentStatus(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<GetExperimentStatusResponse xmlns="http://ilab.mit.edu">
<GetExperimentStatusResult>
<statusReport>
<statusCode>3</statusCode>
<wait>
<effectiveQueueLength>0</effectiveQueueLength>
<estWait>0</estWait>
</wait>
<estRuntime>0</estRuntime>
<estRemainingRuntime>0</estRemainingRuntime>
</statusReport>
<minTimetoLive>0</minTimetoLive>
</GetExperimentStatusResult>
</GetExperimentStatusResponse>
</soap:Body>
</soap:Envelope>"""

    def process_RetrieveResult(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<RetrieveResultResponse xmlns="http://ilab.mit.edu">
<RetrieveResultResult>
<statusCode>3</statusCode>
<experimentResults>&lt;?xml version='1.0' encoding='utf-8' standalone='no' ?&gt;&lt;!DOCTYPE experimentResult SYSTEM 'http://weblab2.mit.edu/xml/experimentResult.dtd'&gt;&lt;experimentResult lab='MIT Microelectronics Weblab' specversion='0.1'&gt;&lt;temp units='K'&gt;+2.97330000E+02&lt;/temp&gt;&lt;datavector name='V1' units='V'&gt;+0.000000E+000 +1.000000E-001 +2.000000E-001 +3.000000E-001 +4.000000E-001 +5.000000E-001 +6.000000E-001 +7.000000E-001 +8.000000E-001 +9.000000E-001 +1.000000E+000 +1.100000E+000 +1.200000E+000 +1.300000E+000 +1.400000E+000 +1.500000E+000 +1.600000E+000 +1.700000E+000 +1.800000E+000 +1.900000E+000 +2.000000E+000&lt;/datavector&gt;&lt;datavector name='I1' units='A'&gt;+2.090000E-011 +1.284000E-008 +1.208000E-007 +9.310000E-007 +7.420000E-006 +6.499000E-005 +5.725000E-004 +4.334000E-003 +1.907000E-002 +4.804000E-002 +8.706000E-002 +9.999000E-002 +1.000100E-001 +1.000100E-001 +1.000200E-001 +1.000100E-001 +1.000000E-001 +1.000000E-001 +1.000000E-001 +1.000100E-001 +9.999000E-002&lt;/datavector&gt;&lt;/experimentResult&gt;</experimentResults>
<xmlResultExtension>Group=,SubmitTime=10/5/2011 7:40:25 PM,ExecutionTime=10/5/2011 7:40:29 PM,EndTime=10/5/2011 7:40:36 PM,ElapsedExecutionTime=7,ElapsedJobTime=11,DeviceName=1N914</xmlResultExtension>
<warningMessages>
<string />
</warningMessages>
<errorMessage />
</RetrieveResultResult>
</RetrieveResultResponse>
</soap:Body>
</soap:Envelope>"""

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

