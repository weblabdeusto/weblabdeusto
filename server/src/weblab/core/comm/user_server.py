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
import weblab.core.comm.user_manager as UPFM

USER_PROCESSING_FACADE_JSON_LISTEN                    = 'core_facade_json_bind'
DEFAULT_USER_PROCESSING_FACADE_JSON_LISTEN            = ''

USER_PROCESSING_FACADE_JSON_PORT                      = 'core_facade_json_port'

USER_PROCESSING_FACADE_SERVER_ROUTE                   = 'core_facade_server_route'
DEFAULT_USER_PROCESSING_SERVER_ROUTE                  = 'default-route-to-server'

class UserProcessingRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):

    FACADE_JSON_LISTEN                           = USER_PROCESSING_FACADE_JSON_LISTEN
    DEFAULT_FACADE_JSON_LISTEN                   = DEFAULT_USER_PROCESSING_FACADE_JSON_LISTEN
    FACADE_JSON_PORT                             = USER_PROCESSING_FACADE_JSON_PORT

    FACADE_SERVER_ROUTE                          = USER_PROCESSING_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE                         = DEFAULT_USER_PROCESSING_SERVER_ROUTE

    def _create_json_remote_facade_manager(self, server, configuration_manager):
        return UPFM.UserProcessingRemoteFacadeManagerJSON( configuration_manager, server)

