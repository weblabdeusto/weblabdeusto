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
import voodoo.gen.exceptions.coordinator.CoordinatorErrors as CoordinatorErrors

class CoordinatorServerError(CoordinatorErrors.CoordinatorError):
    def __init__(self, *args, **kargs):
        CoordinatorErrors.CoordinatorError.__init__(self,*args,**kargs)

class NotASessionTypeError(CoordinatorServerError):
    def __init__(self, *args, **kargs):
        CoordinatorServerError.__init__(self,*args,**kargs)

class BothMapAndMapFileProvidedError(CoordinatorServerError):
    def __init__(self, *args, **kargs):
        CoordinatorServerError.__init__(self,*args,**kargs)

class NeitherMapNorFileProvidedError(CoordinatorServerError):
    def __init__(self, *args, **kargs):
        CoordinatorServerError.__init__(self,*args,**kargs)

class NoServerFoundError(CoordinatorServerError):
    def __init__(self, *args, **kargs):
        CoordinatorServerError.__init__(self,*args,**kargs)

class SessionNotFoundError(CoordinatorServerError):
    def __init__(self, *args, **kargs):
        CoordinatorServerError.__init__(self,*args,**kargs)

class CouldNotCreateSessionError(CoordinatorServerError):
    def __init__(self, msg, exc, *args, **kargs):
        CoordinatorServerError.__init__(self,msg,exc,*args,**kargs)
        self.msg       = msg
        self.exception = exc
