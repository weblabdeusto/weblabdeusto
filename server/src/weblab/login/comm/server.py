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

import weblab.comm.server as RFS
import weblab.login.comm.manager as LFM

LOGIN_FACADE_JSON_LISTEN                    = 'login_facade_json_bind'
DEFAULT_LOGIN_FACADE_JSON_LISTEN            = ''

LOGIN_FACADE_JSON_PORT                      = 'login_facade_json_port'

LOGIN_FACADE_SERVER_ROUTE                   = 'login_facade_server_route'
DEFAULT_LOGIN_SERVER_ROUTE                  = 'default-route-to-server'


class LoginRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):

    FACADE_JSON_LISTEN                           = LOGIN_FACADE_JSON_LISTEN
    DEFAULT_FACADE_JSON_LISTEN                   = DEFAULT_LOGIN_FACADE_JSON_LISTEN
    FACADE_JSON_PORT                             = LOGIN_FACADE_JSON_PORT

    FACADE_SERVER_ROUTE                          = LOGIN_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE                         = DEFAULT_LOGIN_SERVER_ROUTE

    def _create_json_remote_facade_manager(self, server, configuration_manager):
        return LFM.LoginRemoteFacadeManagerJSON( configuration_manager, server )

