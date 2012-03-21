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
#

import weblab.comm.web_server as WebFacadeServer

USERNAME="username"
PASSWORD="password"

class LoginMethod(WebFacadeServer.Method):
    path = '/login/'

    def run(self):
        username = self.get_argument(USERNAME)
        if username is None:
            return "%s argument not provided!" % USERNAME
        password = self.get_argument(PASSWORD)
        if password is None: # Based on IP address
            ip_address = self.get_context().get_ip_address()
            session_id = self.server.login_based_on_client_address(username, ip_address)
            return "%s;%s" % (session_id.id, self.weblab_cookie)
        else:
            session_id = self.server.login(username, password)
            return "%s;%s" % (session_id.id, self.weblab_cookie)

