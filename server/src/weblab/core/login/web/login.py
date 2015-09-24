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
from __future__ import print_function, unicode_literals

import traceback
from flask import make_response

from weblab.core.login.web import weblab_api, get_argument 
from weblab.core.login.exc import InvalidCredentialsError

USERNAME='username'
PASSWORD='password'

@weblab_api.route_login_web('/login/', methods = ['GET', 'POST'])
def login():
    username = get_argument(USERNAME)
    password = get_argument(PASSWORD, 'not provided')

    if username is None:
        return make_response("%s argument not provided!" % USERNAME, 400)

    try:
        session_id = weblab_api.api.login(username, password)
    except InvalidCredentialsError:
        return make_response("Invalid username or password", 403)
    except:
        traceback.print_exc()
        return make_response("There was an unexpected error while logging in.", 500)
    else:
        response = make_response("%s;%s" % (session_id.id, weblab_api.ctx.route))
        session_id_cookie = '%s.%s' % (session_id.id, weblab_api.ctx.route)
        weblab_api.fill_session_cookie(response, session_id_cookie)
        return response

