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

from flask import request, make_response
from weblab.core.wl import weblab_api

@weblab_api.route_web('/language/')
def language():
    accept_language = request.headers.get('Accept-Language')
    if accept_language is None:
        contents = 'var acceptLanguageHeader = null;'
    else:
        contents = 'var acceptLanguageHeader = "%s";' % accept_language
    
    response = make_response(contents)
    response.content_type = 'text/javascript';
    return response
