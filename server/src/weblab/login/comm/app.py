#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2013 onwards University of Deusto
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

import urlparse

from weblab.login.comm.webs import PLUGINS
from werkzeug import Request

from weblab.comm.context import create_context, delete_context
from weblab.configuration_doc import CORE_FACADE_SERVER_ROUTE, CORE_SERVER_URL

class LoginApp(object):

    def __init__(self, cfg_manager, server):
        self.cfg_manager  = cfg_manager
        self.server       = server
        self.server_route = cfg_manager[CORE_FACADE_SERVER_ROUTE]
        url               = cfg_manager.get(CORE_SERVER_URL)
        if url is not None:
            path              = urlparse.urlparse(url).path
            self.location     = path[:path.rfind('/weblab/') + 1]
        else:
            self.location     = '/weblab/'

    def __call__(self, environ, start_response):

        TOKEN = 'login/web'

        path = environ['PATH_INFO']
        relative_path = path[path.find(TOKEN) + len(TOKEN):]

        request = Request(environ)
        create_context(self.server, environ['REMOTE_ADDR'], request.headers)
        try:
            for PluginClass in PLUGINS:
                if relative_path.startswith(PluginClass.path or 'url.not.provided'):
                    plugin = PluginClass(self.cfg_manager, self.server, environ, start_response, self.server_route, self.location)
                    return plugin(environ, start_response)
        finally:
            delete_context()

        # Otherwise
        start_response("404 Not Found", [('Content-Type','text/plain')])
        return ["No plug-in registered for that path."]

