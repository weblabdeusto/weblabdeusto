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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#

import weblab.comm.web_server as WebFacadeServer

from weblab.core.comm.web.upload  import FileUploadMethod
from weblab.core.comm.web.labview import LabViewMethod
from weblab.core.comm.web.client  import ClientMethod
from weblab.core.comm.web.ilab    import ILabMethod
from weblab.core.comm.web.visir   import VisirMethod

from weblab.core.comm.user_server import USER_PROCESSING_FACADE_SERVER_ROUTE, DEFAULT_USER_PROCESSING_SERVER_ROUTE


WEB_FACADE_LISTEN                    = 'core_web_facade_bind'
DEFAULT_WEB_FACADE_LISTEN            = ''

WEB_FACADE_PORT                      = 'core_web_facade_port'

class UserProcessingWebProtocolRemoteFacadeServer(WebFacadeServer.WebProtocolRemoteFacadeServer):
    METHODS = [
                FileUploadMethod,
                LabViewMethod,
                ClientMethod,
                ILabMethod,
                VisirMethod
            ]

class UserProcessingWebRemoteFacadeServer(WebFacadeServer.WebRemoteFacadeServer):
    FACADE_WEB_LISTEN          = WEB_FACADE_LISTEN    
    DEFAULT_FACADE_WEB_LISTEN  = DEFAULT_WEB_FACADE_LISTEN
    FACADE_WEB_PORT            = WEB_FACADE_PORT

    FACADE_SERVER_ROUTE        = USER_PROCESSING_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE       = DEFAULT_USER_PROCESSING_SERVER_ROUTE

    SERVERS = (UserProcessingWebProtocolRemoteFacadeServer,)


