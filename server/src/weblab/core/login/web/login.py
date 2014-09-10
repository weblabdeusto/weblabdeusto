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

from weblab.core.login.web import WebPlugin 
from weblab.login.exc import InvalidCredentialsError

USERNAME="username"
PASSWORD="password"

class LoginPlugin(WebPlugin):

    path = '/login/'

    def __call__(self, environ, start_response):

        username = self.get_argument(USERNAME)

        if username is None:
            return self.build_response("%s argument not provided!" % USERNAME)

        password = self.get_argument(PASSWORD) or 'not provided'
        try:
            session_id = self.server.login(username, password)
        except InvalidCredentialsError:
            return self.build_response("Invalid username or password", code = 403)
        except:
            traceback.print_exc()
            return self.build_response("There was an unexpected error while logging in.", code = 500)
        else:
            self.replace_session(session_id.id)
            return self.build_response("%s;%s" % (session_id.id, self.weblab_cookie))

