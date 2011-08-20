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
import weblab.login.comm.LoginFacadeManager as LFM
try:
    import weblab.login.comm.generated.WebLabDeusto_interface as WebLabDeusto_interface
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

if ZSI_AVAILABLE:
    class LoginRemoteFacadeServerZSI(RFS.AbstractRemoteFacadeServerZSI):
        WebLabDeusto = WebLabDeusto_interface.WebLabDeusto

LOGIN_FACADE_ZSI_LISTEN                     = 'login_facade_soap_bind'
DEFAULT_LOGIN_FACADE_ZSI_LISTEN             = ''

LOGIN_FACADE_ZSI_PORT                       = 'login_facade_soap_port'

LOGIN_FACADE_ZSI_SERVICE_NAME               = 'login_facade_soap_service_name'
DEFAULT_LOGIN_FACADE_ZSI_SERVICE_NAME       = '/weblab/login/soap/'

LOGIN_FACADE_ZSI_PUBLIC_SERVER_HOST         = 'login_facade_soap_public_server_host'
DEFAULT_LOGIN_FACADE_ZSI_PUBLIC_SERVER_HOST = 'www.weblab.deusto.es'
LOGIN_FACADE_ZSI_PUBLIC_SERVER_PORT         = 'login_facade_soap_public_server_port'
DEFAULT_LOGIN_FACADE_ZSI_PUBLIC_SERVER_PORT = 80

LOGIN_FACADE_JSON_LISTEN                    = 'login_facade_json_bind'
DEFAULT_LOGIN_FACADE_JSON_LISTEN            = ''

LOGIN_FACADE_JSON_PORT                      = 'login_facade_json_port'

LOGIN_FACADE_XMLRPC_LISTEN                  = 'login_facade_xmlrpc_bind'
DEFAULT_LOGIN_FACADE_XMLRPC_LISTEN          = ''

LOGIN_FACADE_XMLRPC_PORT                    = 'login_facade_xmlrpc_port'

LOGIN_FACADE_SERVER_ROUTE                   = 'login_facade_server_route'
DEFAULT_LOGIN_SERVER_ROUTE                  = '<route-to-server>'


class LoginRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):

    if ZSI_AVAILABLE:
        SERVERS = RFS.AbstractRemoteFacadeServer.SERVERS + (LoginRemoteFacadeServerZSI,)

    FACADE_ZSI_LISTEN                            = LOGIN_FACADE_ZSI_LISTEN     
    DEFAULT_FACADE_ZSI_LISTEN                    = DEFAULT_LOGIN_FACADE_ZSI_LISTEN                    
    FACADE_ZSI_PORT                              = LOGIN_FACADE_ZSI_PORT                       
    FACADE_ZSI_SERVICE_NAME                      = LOGIN_FACADE_ZSI_SERVICE_NAME                   
    DEFAULT_FACADE_ZSI_SERVICE_NAME              = DEFAULT_LOGIN_FACADE_ZSI_SERVICE_NAME              
    FACADE_ZSI_PUBLIC_SERVER_HOST                = LOGIN_FACADE_ZSI_PUBLIC_SERVER_HOST         
    DEFAULT_FACADE_ZSI_PUBLIC_SERVER_HOST        = DEFAULT_LOGIN_FACADE_ZSI_PUBLIC_SERVER_HOST 
    FACADE_ZSI_PUBLIC_SERVER_PORT                = LOGIN_FACADE_ZSI_PUBLIC_SERVER_PORT         
    DEFAULT_FACADE_ZSI_PUBLIC_SERVER_PORT        = DEFAULT_LOGIN_FACADE_ZSI_PUBLIC_SERVER_PORT 

    FACADE_JSON_LISTEN                           = LOGIN_FACADE_JSON_LISTEN    
    DEFAULT_FACADE_JSON_LISTEN                   = DEFAULT_LOGIN_FACADE_JSON_LISTEN                   
    FACADE_JSON_PORT                             = LOGIN_FACADE_JSON_PORT                      

    FACADE_XMLRPC_LISTEN                         = LOGIN_FACADE_XMLRPC_LISTEN   
    DEFAULT_FACADE_XMLRPC_LISTEN                 = DEFAULT_LOGIN_FACADE_XMLRPC_LISTEN                 
    FACADE_XMLRPC_PORT                           = LOGIN_FACADE_XMLRPC_PORT                    

    FACADE_SERVER_ROUTE                          = LOGIN_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE                         = DEFAULT_LOGIN_SERVER_ROUTE

    if ZSI_AVAILABLE:
        def _create_zsi_remote_facade_manager(self, server, configuration_manager):
            return LFM.LoginRemoteFacadeManagerZSI( configuration_manager, server )

    def _create_xmlrpc_remote_facade_manager(self, server, configuration_manager):
        return LFM.LoginRemoteFacadeManagerXMLRPC( configuration_manager, server )

    def _create_json_remote_facade_manager(self, server, configuration_manager):
        return LFM.LoginRemoteFacadeManagerJSON( configuration_manager, server )

