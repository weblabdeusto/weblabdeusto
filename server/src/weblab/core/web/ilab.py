#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005 onwards University of Deusto
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
from __future__ import print_function, unicode_literals

from flask import request, make_response
from weblab.core.wl import weblab_api

import json
import traceback

from weblab.data.experiments import ExperimentId

from weblab.core.coordinator.clients.ilab_batch import RequestSerializer

serializer = RequestSerializer()

@weblab_api.route_web('/ilab/')
def ilab():
    action = request.headers.get('SOAPAction')
    if action is None:
        return "No SOAPAction provided"

    if weblab_api.ctx.session_id is None:
        return "Not logged in!"

    if weblab_api.ctx.reservation_id is None:
        try:
            reservation_id_str = weblab_api.api.get_reservation_id_by_session_id()
            weblab_api.ctx.reservation_id = reservation_id_str
        except:
            traceback.print_exc()

    methods = {
        '"http://ilab.mit.edu/GetLabConfiguration"'      : process_GetLabConfiguration,
        '"http://ilab.mit.edu/Submit"'                   : process_Submit,
        '"http://ilab.mit.edu/GetExperimentStatus"'      : process_GetExperimentStatus,
        '"http://ilab.mit.edu/RetrieveResult"'           : process_RetrieveResult,
        '"http://ilab.mit.edu/SaveAnnotation"'           : process_SaveAnnotation,
        '"http://ilab.mit.edu/ListAllClientItems"'       : process_ListAllClientItems,
        '"http://ilab.mit.edu/LoadClientItem"'           : process_LoadClientItem,
        '"http://ilab.mit.edu/SaveClientItem"'           : process_SaveClientItem,
        '"http://ilab.mit.edu/GetExperimentInformation"' : process_GetExperimentInformation,
    }

    if not action in methods:
        return "Action not found"

    response = make_response(methods[action]())
    response.content_type = 'text/xml'
    if hasattr(weblab_api.ctx, 'other_cookies'):
        for name, value in weblab_api.ctx.other_cookies:
            response.set_cookie(name, value, path = weblab_api.ctx.location)
    return response

def process_GetLabConfiguration(self):
    lab_server_id = serializer.parse_get_lab_configuration_request(request.data)
    ilab_request = {
        'operation' : 'get_lab_configuration',
    }
    # TODO: client address
    reservation_status = weblab_api.api.reserve_experiment(ExperimentId(lab_server_id, 'iLab experiments'), json.dumps(ilab_request), '{}')
    lab_configuration = reservation_status.initial_data
    return serializer.generate_lab_configuration_response(lab_configuration)

def process_Submit(self):
    lab_server_id, experiment_specification, _, _ = serializer.parse_submit_request(request.data)
    ilab_request = {
        'operation' : 'submit',
        'payload'   : experiment_specification
    }
    reservation_status = weblab_api.api.reserve_experiment(ExperimentId(lab_server_id, 'iLab experiments'), json.dumps(ilab_request), '{}')
    weblab_api.ctx.other_cookies = {'weblab_reservation_id' : reservation_status.reservation_id.id}

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

    reservation_status = weblab_api.api.get_reservation_status()
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
    if self.reservation_id is None:
        return "Reservation id not found in cookie"

    reservation_status = weblab_api.api.get_reservation_status()
    try:
        response = json.loads(reservation_status.initial_data)
    except:
        return "Error occurred: %s" % reservation_status.initial_data

    code       = response['code']
    results    = response['results']
    xmlResults = response['xmlResults']

    return serializer.generate_retrieve_result_response(code, results, xmlResults)

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

