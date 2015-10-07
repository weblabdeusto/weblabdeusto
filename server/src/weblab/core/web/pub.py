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

import os
from flask import send_from_directory
from weblab.core.wl import weblab_api

@weblab_api.route_web('/pub/')
def pub_index():
    return "This is the public directory, in the 'pub' of your deployment, if it exists."

@weblab_api.route_web('/pub/<path:path>')
def pub(path = ''):
    deployment_dir = os.path.abspath(weblab_api.config.get('deployment_dir'))
    base_directory = os.path.join(deployment_dir, 'pub')
    return send_from_directory(base_directory, path)

