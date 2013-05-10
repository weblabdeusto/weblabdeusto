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

class WebPlugin(object):

    path = None # To be defined by the subclasses

    def __init__(self, cfg_manager, server, environ):
        self.cfg_manager = cfg_manager
        self.server      = server
        self.environ     = environ
        self._contents   = None

        # TODO: 
        self.weblab_cookie = 'testing...'

    @property
    def contents(self):
        if self.environ.get('REQUEST_METHOD','GET') not in ('POST', 'PUT'):
            return None

        if self._contents is not None:
            return self._contents

        try:
            length = int(self.environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            length = 0

        contents = environ['wsgi.input'].read(length)
        self._contents = contents
        return contents

    def get_argument(self, name):
        qs = self.environ['QUERY_STRING']
        get_args = urlparse.parse_qs(qs)
        if name in get_args:
            return get_args[name][0]

        if self.contents is not None:
            post_args = urlparse.parse_qs(self.contents)
            if name in post_args:
                return post_args[name][0]

        return None



from weblab.login.comm.webs.login import LoginPlugin

PLUGINS = [
    LoginPlugin,
]
