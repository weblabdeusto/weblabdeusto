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

import weblab.comm.RemoteFacadeServer as RFS
import weblab.core.comm.UserProcessingFacadeManager as UPFM

try:
    import weblab.core.comm.generated.WebLabDeusto_interface as WebLabDeusto_interface
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

USER_PROCESSING_FACADE_ZSI_LISTEN                     = 'core_facade_soap_bind'
DEFAULT_USER_PROCESSING_FACADE_ZSI_LISTEN             = ''

USER_PROCESSING_FACADE_ZSI_PORT                       = 'core_facade_soap_port'

USER_PROCESSING_FACADE_ZSI_SERVICE_NAME               = 'core_facade_soap_service_name'
DEFAULT_USER_PROCESSING_FACADE_ZSI_SERVICE_NAME       = '/weblab/soap/'

USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_HOST         = 'core_facade_soap_public_server_host'
DEFAULT_USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_HOST = 'www.weblab.deusto.es'
USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_PORT         = 'core_facade_soap_public_server_port'
DEFAULT_USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_PORT = 80

USER_PROCESSING_FACADE_JSON_LISTEN                    = 'core_facade_json_bind'
DEFAULT_USER_PROCESSING_FACADE_JSON_LISTEN            = ''

USER_PROCESSING_FACADE_JSON_PORT                      = 'core_facade_json_port'

USER_PROCESSING_FACADE_XMLRPC_LISTEN                  = 'core_facade_xmlrpc_bind'
DEFAULT_USER_PROCESSING_FACADE_XMLRPC_LISTEN          = ''

USER_PROCESSING_FACADE_XMLRPC_PORT                    = 'core_facade_xmlrpc_port'

USER_PROCESSING_FACADE_SERVER_ROUTE                   = 'core_facade_server_route'
DEFAULT_USER_PROCESSING_SERVER_ROUTE                  = '<route-to-server>'

class UserProcessingRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):

    if ZSI_AVAILABLE:
        class RemoteFacadeServerZSI(RFS.AbstractRemoteFacadeServerZSI):
            WebLabDeusto = WebLabDeusto_interface.WebLabDeusto
        SERVERS = RFS.AbstractRemoteFacadeServer.SERVERS + (RemoteFacadeServerZSI,)

    FACADE_ZSI_LISTEN                            = USER_PROCESSING_FACADE_ZSI_LISTEN   
    DEFAULT_FACADE_ZSI_LISTEN                    = DEFAULT_USER_PROCESSING_FACADE_ZSI_LISTEN   
    FACADE_ZSI_PORT                              = USER_PROCESSING_FACADE_ZSI_PORT                       
    FACADE_ZSI_SERVICE_NAME                      = USER_PROCESSING_FACADE_ZSI_SERVICE_NAME                 
    DEFAULT_FACADE_ZSI_SERVICE_NAME              = DEFAULT_USER_PROCESSING_FACADE_ZSI_SERVICE_NAME                
    FACADE_ZSI_PUBLIC_SERVER_HOST                = USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_HOST         
    DEFAULT_FACADE_ZSI_PUBLIC_SERVER_HOST        = DEFAULT_USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_HOST 
    FACADE_ZSI_PUBLIC_SERVER_PORT                = USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_PORT         
    DEFAULT_FACADE_ZSI_PUBLIC_SERVER_PORT        = DEFAULT_USER_PROCESSING_FACADE_ZSI_PUBLIC_SERVER_PORT 

    FACADE_JSON_LISTEN                           = USER_PROCESSING_FACADE_JSON_LISTEN    
    DEFAULT_FACADE_JSON_LISTEN                   = DEFAULT_USER_PROCESSING_FACADE_JSON_LISTEN                   
    FACADE_JSON_PORT                             = USER_PROCESSING_FACADE_JSON_PORT                      

    FACADE_XMLRPC_LISTEN                         = USER_PROCESSING_FACADE_XMLRPC_LISTEN   
    DEFAULT_FACADE_XMLRPC_LISTEN                 = DEFAULT_USER_PROCESSING_FACADE_XMLRPC_LISTEN                 
    FACADE_XMLRPC_PORT                           = USER_PROCESSING_FACADE_XMLRPC_PORT                   

    FACADE_SERVER_ROUTE                          = USER_PROCESSING_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE                         = DEFAULT_USER_PROCESSING_SERVER_ROUTE

    if ZSI_AVAILABLE:
        def _create_zsi_remote_facade_manager(self, server, configuration_manager):
            return UPFM.UserProcessingRemoteFacadeManagerZSI( configuration_manager, server)

    def _create_xmlrpc_remote_facade_manager(self, server, configuration_manager):
        return UPFM.UserProcessingRemoteFacadeManagerXMLRPC( configuration_manager, server)

    def _create_json_remote_facade_manager(self, server, configuration_manager):
        return UPFM.UserProcessingRemoteFacadeManagerJSON( configuration_manager, server)

