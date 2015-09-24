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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import os

from flask import request, send_file

from weblab.util import data_filename
from weblab.core.wl import weblab_api
import weblab.configuration_doc as configuration_doc

def logo_impl(logo_path):
    logo_path = os.path.abspath(logo_path)
    if not os.path.exists(logo_path):
        print("Error:", logo_path, "not found")
        logo_path = data_filename("weblab/admin/logo-not-found.jpg")
    response = send_file(logo_path, as_attachment = False, conditional = True, add_etags = True, cache_timeout=0)
    response.headers['Cache-Control'] = 'max-age=0'
    return response
   

@weblab_api.route_web('/logos/regular')
def logo():
    logo_path = weblab_api.config[configuration_doc.CORE_LOGO_PATH]
    return logo_impl(logo_path)

@weblab_api.route_web('/logos/small')
def logo_small():
    logo_path = weblab_api.config[configuration_doc.CORE_LOGO_SMALL_PATH]
    return logo_impl(logo_path)

