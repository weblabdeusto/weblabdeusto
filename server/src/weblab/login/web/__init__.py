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
from weblab.comm.context import get_context

from werkzeug import HTTP_STATUS_CODES

from abc import ABCMeta, abstractmethod

class ExternalSystemManager(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user(self, credentials):
        """Create a User instance with the data of this user."""

    @abstractmethod
    def get_user_id(self, credentials):
        """Create a string which is a unique identifier for this user in the foreign system"""

class WebPlugin(object):

    path = None # To be defined by the subclasses

    def __init__(self, cfg_manager, server, environ, start_response, server_route, location):
        self.cfg_manager = cfg_manager
        self.server      = server
        self.environ     = environ
        self.start_response = start_response
        self._contents   = None

        self.server_route  = server_route
        self.location      = location

        self.weblab_cookie = None
        self.login_weblab_cookie = None

        for current_cookie in environ.get('HTTP_COOKIE','').split('; '):
            if current_cookie.startswith('weblabsessionid'):
                self.weblab_cookie = current_cookie
            if current_cookie.startswith('loginweblabsessionid'):
                self.login_weblab_cookie = current_cookie

        if self.weblab_cookie is None:
            if self.server_route is not None:
                self.weblab_cookie = "weblabsessionid=sessidnotfound.%s" % self.server_route
            else:
                self.weblab_cookie = "weblabsessionid=sessidnotfound"

        self.weblab_session = self.weblab_cookie.split('=')[1]

        if self.login_weblab_cookie is None:
            if self.server_route is not None:
                self.login_weblab_cookie = "loginweblabsessionid=loginsessid.not.found.%s" % self.server_route
            else:
                self.login_weblab_cookie = "loginweblabsessionid=sessidnotfound"

    @classmethod
    def initialize(klass, cfg_manager, route):
        pass

    def replace_session(self, session_id):
        old_weblab_session = self.weblab_session
        if self.server_route is not None:
            self.weblab_session = '%s.%s' % (session_id, self.server_route)
        else:
            self.weblab_session = session_id

        self.weblab_cookie  = self.weblab_cookie.replace(old_weblab_session, self.weblab_session)

    @property
    def weblab_cookies(self):
        return ('Set-Cookie', 'weblabsessionid=%s; path=%s' % (self.weblab_session, self.location))

    @property
    def context(self):
        return get_context()

    @property
    def headers(self):
        return get_context().headers

    @property
    def uri(self):
        return self.environ['PATH_INFO']

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

        contents = self.environ['wsgi.input'].read(length)
        self._contents = contents
        return contents

    @property
    def relative_path(self):
        full_path = self.environ['PATH_INFO']
        return full_path[full_path.find(self.path) + len(self.path):]

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

    def build_response(self, text, content_type = 'text/plain', code = 200, headers = []):
        full_code = '%s %s' % (code, HTTP_STATUS_CODES.get(code, ''))
        self.start_response(full_code, [('Content-Type', content_type), self.weblab_cookies] + list(headers))
        return [ text ]

#########################################################
# 
#     Registry of the web plug-ins and User Auths
# 

from weblab.login.web.login      import LoginPlugin
from weblab.login.web.facebook   import FacebookPlugin, FacebookManager
from weblab.login.web.openid_web import OpenIdPlugin, OpenIdManager

WEB_PLUGINS = [
    LoginPlugin,
    FacebookPlugin,
    OpenIdPlugin,
    # Your plug-in here
]

EXTERNAL_MANAGERS = {
    FacebookManager.NAME : FacebookManager(),
    OpenIdManager.NAME   : OpenIdManager(),
    # Your plug-in here
}
