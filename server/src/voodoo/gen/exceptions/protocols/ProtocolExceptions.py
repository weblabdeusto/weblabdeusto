#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import voodoo.gen.exceptions.exceptions as genExceptions

class ProtocolException(genExceptions.GeneratorException):
    def __init__(self,*args,**kargs):
        genExceptions.GeneratorException.__init__(self,*args,**kargs)

# Generic exceptions

class RemoteException(ProtocolException):
    """ Every exception generated at protocol level must implement this class. This 
    way, the locator systems knows whether the exception was propagated from the server
    or it was generated due to a communication problem (since it will try to call the 
    server again if it's the last case)
    """
    def __init__(self, msg, exception,*args,**kargs):
        ProtocolException.__init__(self,msg,*args,**kargs)
        self.msg = msg
        self.cause_exception = exception

class UnknownRemoteException(RemoteException):
    def __init__(self, msg, exception, *args, **kargs):
        RemoteException.__init__(self,msg,exception,*args,**kargs)

# Client Exceptions

class ClientProtocolException(ProtocolException):
    def __init__(self,*args,**kargs):
        ProtocolException.__init__(self,*args,**kargs)

class ClientCreationException(ClientProtocolException):
    def __init__(self,*args,**kargs):
        ClientProtocolException.__init__(self,*args,**kargs)

class ClientInstanciationException(ClientCreationException):
    def __init__(self,*args,**kargs):
        ClientCreationException.__init__(self,*args,**kargs)

class ClientClassCreationException(ClientCreationException):
    def __init__(self,*args,**kargs):
        ClientCreationException.__init__(self,*args,**kargs)

# Server Exceptions

class ServerProtocolException(ProtocolException):
    def __init__(self,*args,**kargs):
        ProtocolException.__init__(self,*args,**kargs)

class InvalidServerParameterException(ServerProtocolException):
    def __init__(self,*args,**kargs):
        ServerProtocolException.__init__(self,*args,**kargs)

