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

import weblab.facade.RemoteFacadeServer as RFS
import weblab.core.facade.AdminFacadeManager as AFM
from weblab.core.facade.AdminFacadeServerSmartGWT import AdminFacadeServerSmartGWT

from weblab.core.facade.UserProcessingFacadeServer import USER_PROCESSING_FACADE_SERVER_ROUTE, DEFAULT_USER_PROCESSING_SERVER_ROUTE

ADMIN_FACADE_JSON_LISTEN                    = 'admin_facade_json_bind'
DEFAULT_ADMIN_FACADE_JSON_LISTEN            = ''

ADMIN_FACADE_JSON_PORT                      = 'admin_facade_json_port'

class AdminRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):
    FACADE_JSON_LISTEN                           = ADMIN_FACADE_JSON_LISTEN    
    DEFAULT_FACADE_JSON_LISTEN                   = DEFAULT_ADMIN_FACADE_JSON_LISTEN                   
    FACADE_JSON_PORT                             = ADMIN_FACADE_JSON_PORT                      

    FACADE_SERVER_ROUTE                          = USER_PROCESSING_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE                         = DEFAULT_USER_PROCESSING_SERVER_ROUTE

    SERVERS = (AdminFacadeServerSmartGWT,)

    def _create_smartgwt_remote_facade_manager(self, server, configuration_manager):
        return AFM.AdminRemoteFacadeManagerJSON( configuration_manager, server)

