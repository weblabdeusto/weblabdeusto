#!/usr/bin/python
# -*- coding: utf-8 -*-
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

"""
This module contains the Login Server. This server will only
manage the authentication (and not the authorization) of the 
users. To this end, it defines that there are two interfaces:

 * One for those systems that can be checked with typical credentials (e.g.,
   using a username a password). Examples of this would be a regular database,
   a LDAP server, or a set of constraints such as "is the user coming from 
   this IP address?". This interface is called "SimpleAuthn".

 * The system, which manages that there is an external system that manages
   the authentication, and some external protocol is required. Examples of this
   are OAuth, OpenID or similar. They all require using a web interface. This
   interface is called "WebProtocolAuthn".

The LoginServer manages both interfaces.
"""

import voodoo.log as log
from voodoo.log import logged

import weblab.login.comm.server as LoginFacadeServer
import weblab.login.comm.wsgi_server as wsgi_server

import weblab.data.server_type as ServerType

# TODO list:
# - Remove this file completely


class LoginServer(object):

    FACADE_SERVERS = ( LoginFacadeServer.LoginRemoteFacadeServer, wsgi_server.LoginWsgiRemoteFacadeServer )

    def __init__(self, coord_address, locator, cfg_manager, dont_start = False, *args, **kwargs):
        super(LoginServer,self).__init__(*args, **kwargs)

        log.log( LoginServer, log.level.Info, "Starting Login Server")

        self._locator       = locator
        self._cfg_manager   = cfg_manager

        self._facade_servers       = []

        if not dont_start:
            for ServerClass in self.FACADE_SERVERS:
                self._facade_servers.append(ServerClass( self, cfg_manager ))

            for server in self._facade_servers:
                server.start()

    def stop(self):
        if hasattr(super(LoginServer, self), 'stop'):
            super(LoginServer, self).stop()
        for server in self._facade_servers:
            server.stop()

    @logged(log.level.Info, except_for='password')
    def login(self, username, password):
        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        return ups_server.login(username, password)

    @logged(log.level.Info)
    def extensible_login(self, system, credentials):
        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        return ups_server.extensible_login(system, credentials)

    @logged(log.level.Info, except_for="password")
    def grant_external_credentials(self, username, password, system, credentials):
        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        return ups_server.grant_external_credentials(username, password, system, credentials)

    @logged(log.level.Info)
    def create_external_user(self, system, credentials):
        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        return ups_server.create_external_user(system, credentials)

