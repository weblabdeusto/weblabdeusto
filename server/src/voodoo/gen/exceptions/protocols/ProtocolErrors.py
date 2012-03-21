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

import voodoo.gen.exceptions.exceptions as genErrors

class ProtocolError(genErrors.GeneratorError):
    def __init__(self,*args,**kargs):
        genErrors.GeneratorError.__init__(self,*args,**kargs)

# Generic exceptions

class RemoteError(ProtocolError):
    """ Every exception generated at protocol level must implement this class. This
    way, the locator systems knows whether the exception was propagated from the server
    or it was generated due to a communication problem (since it will try to call the
    server again if it's the last case)
    """
    def __init__(self, msg, exception,*args,**kargs):
        ProtocolError.__init__(self,msg,*args,**kargs)
        self.msg = msg
        self.cause_exception = exception

class UnknownRemoteError(RemoteError):
    def __init__(self, msg, exception, *args, **kargs):
        RemoteError.__init__(self,msg,exception,*args,**kargs)

# Client Exceptions

class ClientProtocolError(ProtocolError):
    def __init__(self,*args,**kargs):
        ProtocolError.__init__(self,*args,**kargs)

class ClientCreationError(ClientProtocolError):
    def __init__(self,*args,**kargs):
        ClientProtocolError.__init__(self,*args,**kargs)

class ClientInstanciationError(ClientCreationError):
    def __init__(self,*args,**kargs):
        ClientCreationError.__init__(self,*args,**kargs)

class ClientClassCreationError(ClientCreationError):
    def __init__(self,*args,**kargs):
        ClientCreationError.__init__(self,*args,**kargs)

# Server Exceptions

class ServerProtocolError(ProtocolError):
    def __init__(self,*args,**kargs):
        ProtocolError.__init__(self,*args,**kargs)

class InvalidServerParameterError(ServerProtocolError):
    def __init__(self,*args,**kargs):
        ServerProtocolError.__init__(self,*args,**kargs)

