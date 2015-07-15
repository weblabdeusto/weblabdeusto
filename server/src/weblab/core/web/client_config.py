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

import urlparse

from flask import jsonify
from weblab.core.wl import weblab_api
import weblab.configuration_doc as configuration_doc

@weblab_api.route_web('/client_config.json')
def client_configuration():
    contents = weblab_api.db.client_configuration()
    url = weblab_api.config[configuration_doc.CORE_SERVER_URL]
    path = urlparse.urlparse(url).path # /foo/weblab/
    contents['base.location'] = path.rsplit('/weblab/', 1)[0]
    if not contents.get('demo.available'):
        contents.pop('demo.username', None)
        contents.pop('demo.password', None)
    return jsonify(contents)
