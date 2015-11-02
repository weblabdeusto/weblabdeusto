#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Luis Rodriguez Gil <luis.rodriguezgil@deusto.es>
#
from flask import make_response, request
from weblab.core.wl import weblab_api

import uuid
import json


# TO-DO: Just a prototype.
import requests

JOBS = {}


@weblab_api.route_web('/compiserv/')
def compiserve():
    msg = "Welcome to the Compiler Service. This is not yet implemented."
    data = {"msg": msg}
    contents = json.dumps(data, indent = 4)
    response = make_response(contents)
    response.content_type = 'application/json'
    return response


@weblab_api.route_web('/compiserv/queue/armc', methods=["POST"])
def compiserve_queue_vhdl_post():
    """
    Enqueues a VHDL synthesization job. This can be done by any client.
    :return:
    """
    BASE_URL = "http://llcompilerservice.azurewebsites.net/CompilerGeneratorService.svc"
    POST_URL = BASE_URL + "/PutCompilerTask/uvision"

    response = {
        "result": ""  # accepted or denied
    }

    file_contents = None

    if request.data is not None:
        file_contents = request.data
    elif request.files is not None and len(request.files) > 0:
        file_contents = request.files['file']
        # TO-DO

    if file_contents is None:
        response['result'] = 'denied'
        response['reason'] = 'no_file_sent'

    else:
        # Send to AZURE SERVICE
        resp = requests.post(POST_URL, file_contents)
        json_resp = resp.json()
        generated_date = json_resp["GeneratedDate"]
        id = json_resp["ID"]
        token = json_resp["TokenID"]

        response['result'] = 'accepted'
        response['uid'] = id + "+" + token
        # response['uid'] = uuid.uuid1()

    contents = json.dumps(response, indent=4)
    response = make_response(contents)
    response.content_type = 'application/json'
    return response


@weblab_api.route_web('/compiserv/queue/<uid>', methods=["GET"])
def compiserve_queue_get(uid):
    """
    Enquiries about the status of a specific job. This can be done by any client.
    :return:
    """
    result = {
        "result": ""
    }

    if uid not in JOBS:
        result['state'] = 'not_found'

    job = JOBS[uid]

    if job['state'] == 'done':
        result['state'] = 'done'

    elif job['state'] == 'failed':
        result['failed'] = 'failed'

    else:
        # TODO
        result['state'] = 'queued'
        result['position'] = 2

    contents = json.dumps(result, indent=4)
    response = make_response(contents)
    response.content_type = 'application/json'
    return response


@weblab_api.route_web('/compiserv/result/<uid>/outputfile', methods=["GET"])
def compiserve_result_outputfile(uid):
    """
    Requests the result (outputfile) of a job. This is only to be called INTERNALLY by the Experiment Servers
    and is protected by a token.
    :return:
    """

    if True:  # TODO: IF FILE IS INDEED READY
        file_contents = """ TEST FILE """
        response = make_response(file_contents)
        response.headers["Content-Disposition"] = "attachment; filename=result.bin"
        response.headers["Content-Type"] = "application/octet-stream"
    else:  #
        result = {
            'result': 'error',
            'msg': 'result not found'
        }
        response = make_response(result)
        response.headers["Content-Type"] = "application/json"

    return response

@weblab_api.route_web('/compiserv/result/<uid>/logfile', methods=["GET"])
def compiserve_result_logfile(uid):
    """
    Requests the result (logfile) of a job. This is only to be called INTERNALLY by the Experiment Servers
    and is protected by a token.
    :param uid:
    :return:
    """

    if True:  # TODO: IF FILE IS INDEED READY
        file_contents = """ TEST LOG FILE """
        response = make_response(file_contents)
        response.headers["Content-Disposition"] = "attachment; filename=result.log"
        response.headers["Content-Type"] = "application/octet-stream"
    else:  #
        result = {
            'result': 'error',
            'msg': 'result not found'
        }
        response = make_response(result)
        response.headers["Content-Type"] = "application/json"

    return response
