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

from weblab.login.comm.webs import WebPlugin 
from weblab.login.exc import InvalidCredentialsError

USERNAME="username"
PASSWORD="password"

class LoginPlugin(WebPlugin):

    path = '/login/'

    def __call__(self, environ, start_response):

        username = self.get_argument(USERNAME)

        if username is None:
            start_response("200 OK", [('Content-Type','text/plain')])
            return "%s argument not provided!" % USERNAME

        password = self.get_argument(PASSWORD)
        if password is None:
            # TODO: get_context not implemented
            ip_address = self.get_context().get_ip_address()
            session_id = self.server.login_based_on_client_address(username, ip_address)
            return "%s;%s" % (session_id.id, self.weblab_cookie)

        try:
            session_id = self.server.login(username, password)
        except InvalidCredentialsError:
            start_response("403 Forbidden", [('Content-Type','text/plain')])
            return [ "Invalid username or password" ]
        except:
            start_response("500 Server error", [('Content-Type','text/plain')])
            return [ "There was an unexpected error while logging in." ]
        else:
            start_response("200 OK", [('Content-Type','text/plain')])
            return [ "%s;%s" % (session_id.id, self.weblab_cookie) ]

