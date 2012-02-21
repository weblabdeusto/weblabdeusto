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

class LocatorError(genErrors.GeneratorError):
    def __init__(self,*args,**kargs):
        genErrors.GeneratorError.__init__(self,*args,**kargs)

class UnableToCompleteOperationError(LocatorError):
    def __init__(self, *args, **kwargs):
        LocatorError.__init__(self, *args, **kwargs)

class ServerFoundInCacheError(LocatorError):
    def __init__(self,server,*args,**kargs):
        self._server = server
        LocatorError.__init__(self,*args,**kargs)
    def get_server(self):
        return self._server

class NoServerFoundError(LocatorError):
    def __init__(self,*args,**kargs):
        LocatorError.__init__(self,*args,**kargs)

class NotAServerTypeError(LocatorError):
    def __init__(self,*args,**kargs):
        LocatorError.__init__(self,*args,**kargs)

class InvalidListOfMethodsError(LocatorError):
    def __init__(self,*args,**kargs):
        LocatorError.__init__(self,*args,**kargs)

class MoreServersThanExpectedError(LocatorError):
    def __init__(self,*args,**kargs):
        LocatorError.__init__(self,*args,**kargs)

class NoSuchServerTypeFoundError(LocatorError):
    def __init__(self,*args,**kargs):
        LocatorError.__init__(self,*args,**kargs)

class ProblemCommunicatingWithCoordinatorError(LocatorError):
    def __init__(self,msg,exc,*args,**kargs):
        LocatorError.__init__(self,msg,exc,*args,**kargs)
        self.msg = msg
        self.cause_exception = exc

class NoNetworkAvailableError(LocatorError):
    def __init__(self, *args, **kargs):
        LocatorError.__init__(self, *args, **kargs)
