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
import json
from flask import make_response
from weblab.core.wl import weblab_api


@weblab_api.route_web('/compiserv/')
def compiserve():
    msg = "Welcome to the Compiler Service. This is not yet implemented."
    data = {"msg": msg}
    contents = json.dumps(data, indent = 4)
    response = make_response(contents)
    response.content_type = 'application/json'
    return response


@weblab_api.route_web('/compiserv/vhdl')
def compiserve_vhdl():
    pass