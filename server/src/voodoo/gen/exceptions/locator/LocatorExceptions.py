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

class LocatorException(genExceptions.GeneratorException):
    def __init__(self,*args,**kargs):
        genExceptions.GeneratorException.__init__(self,*args,**kargs)

class UnableToCompleteOperationException(LocatorException):
    def __init__(self, *args, **kwargs):
        LocatorException.__init__(self, *args, **kwargs)

class ServerFoundInCacheException(LocatorException):
    def __init__(self,server,*args,**kargs):
        self._server = server
        LocatorException.__init__(self,*args,**kargs)
    def get_server(self):
        return self._server

class NoServerFoundException(LocatorException):
    def __init__(self,*args,**kargs):
        LocatorException.__init__(self,*args,**kargs)

class NotAServerTypeException(LocatorException):
    def __init__(self,*args,**kargs):
        LocatorException.__init__(self,*args,**kargs)

class InvalidListOfMethodsException(LocatorException):
    def __init__(self,*args,**kargs):
        LocatorException.__init__(self,*args,**kargs)

class MoreServersThanExpectedException(LocatorException):
    def __init__(self,*args,**kargs):
        LocatorException.__init__(self,*args,**kargs)

class NoSuchServerTypeFoundException(LocatorException):
    def __init__(self,*args,**kargs):
        LocatorException.__init__(self,*args,**kargs)

class ProblemCommunicatingWithCoordinatorException(LocatorException):
    def __init__(self,msg,exc,*args,**kargs):
        LocatorException.__init__(self,msg,exc,*args,**kargs)
        self.msg = msg
        self.cause_exception = exc

class NoNetworkAvailableException(LocatorException):
    def __init__(self, *args, **kargs):
        LocatorException.__init__(self, *args, **kargs)
