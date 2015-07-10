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

@weblab_api.route_web('/logos/regular')
def logo():
    logo_path = weblab_api.config[configuration_doc.CORE_LOGO_PATH]
    logo_path = os.path.abspath(logo_path)
    if not os.path.exists(logo_path):
        print("Error:", logo_path, "not found")
        logo_path = data_filename("weblab/admin/logo-not-found.jpg")
    return send_file(logo_path)

@weblab_api.route_web('/logos/mobile')
def logo_mobile():
    logo_path = weblab_api.config[configuration_doc.CORE_LOGO_MOBILE_PATH]
    logo_path = os.path.abspath(logo_path)
    if not os.path.exists(logo_path):
        print("Error:",logo_path, "not found")
        logo_path = data_filename("weblab/admin/logo-not-found.jpg")
    return send_file(logo_path)
