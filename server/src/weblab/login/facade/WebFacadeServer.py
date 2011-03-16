#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005-2009 University of Deusto
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

import weblab.facade.WebFacadeServer as WebFacadeServer

from weblab.login.facade.LoginFacadeServer import LOGIN_FACADE_SERVER_ROUTE, DEFAULT_LOGIN_SERVER_ROUTE


WEB_FACADE_LISTEN                    = 'login_web_facade_bind'
DEFAULT_WEB_FACADE_LISTEN            = ''

WEB_FACADE_PORT                      = 'login_web_facade_port'

class LoginWebProtocolRemoteFacadeServer(WebFacadeServer.WebProtocolRemoteFacadeServer):
    METHODS = [] # TODO

class LoginWebRemoteFacadeServer(WebFacadeServer.WebRemoteFacadeServer):
    FACADE_WEB_LISTEN          = WEB_FACADE_LISTEN    
    DEFAULT_FACADE_WEB_LISTEN  = DEFAULT_WEB_FACADE_LISTEN
    FACADE_WEB_PORT            = WEB_FACADE_PORT

    FACADE_SERVER_ROUTE        = LOGIN_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE       = DEFAULT_LOGIN_SERVER_ROUTE

    SERVERS = (LoginWebProtocolRemoteFacadeServer,)


