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

import datetime
from flask import request, make_response
import traceback

from weblab.core.login.web import WebPlugin, weblab_api, get_argument 
from weblab.core.login.exc import InvalidCredentialsError

USERNAME="username"
PASSWORD="password"

@weblab_api.route_login_web('/login/', methods = ['GET', 'POST'])
def login():
    import weblab.core.server as core_api
    username = get_argument(USERNAME)
    password = get_argument(PASSWORD, 'not provided')

    if username is None:
        return "%s argument not provided!" % USERNAME

    try:
        session_id = core_api.login(username, password)
    except InvalidCredentialsError:
        return make_response("Invalid username or password", 403)
    except:
        traceback.print_exc()
        return make_response("There was an unexpected error while logging in.", 500)
    else:
        response = make_response("%s;%s" % (session_id.id, weblab_api.ctx.route))
        session_id_cookie = '%s.%s' % (session_id.id, weblab_api.ctx.route)
        now = datetime.datetime.now()
        response.set_cookie('weblabsessionid', session_id_cookie, expires = now + datetime.timedelta(days = 100), path = weblab_api.ctx.location)
        response.set_cookie('loginweblabsessionid', session_id_cookie, expires = now + datetime.timedelta(hours = 1), path = weblab_api.ctx.location)

        return response

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

