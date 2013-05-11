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

import traceback

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

        password = self.get_argument(PASSWORD) or 'not provided'
        try:
            session_id = self.server.login(username, password)
        except InvalidCredentialsError:
            start_response("403 Forbidden", [('Content-Type','text/plain')])
            return [ "Invalid username or password" ]
        except:
            traceback.print_exc()
            start_response("500 Server error", [('Content-Type','text/plain')])
            return [ "There was an unexpected error while logging in." ]
        else:
            self.replace_session(session_id.id)
            start_response("200 OK", [('Content-Type','text/plain'), self.weblab_cookies])
            return [ "%s;%s" % (session_id.id, self.weblab_cookie) ]

