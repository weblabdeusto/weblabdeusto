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
import voodoo.gen.exceptions.coordinator.CoordinatorExceptions as CoordinatorExceptions

class CoordinatorServerException(CoordinatorExceptions.CoordinatorException):
    def __init__(self, *args, **kargs):
        CoordinatorExceptions.CoordinatorException.__init__(self,*args,**kargs)

class NotASessionTypeException(CoordinatorServerException):
    def __init__(self, *args, **kargs):
        CoordinatorServerException.__init__(self,*args,**kargs)

class BothMapAndMapFileProvidedException(CoordinatorServerException):
    def __init__(self, *args, **kargs):
        CoordinatorServerException.__init__(self,*args,**kargs)

class NeitherMapNorFileProvidedException(CoordinatorServerException):
    def __init__(self, *args, **kargs):
        CoordinatorServerException.__init__(self,*args,**kargs)

class NoServerFoundException(CoordinatorServerException):
    def __init__(self, *args, **kargs):
        CoordinatorServerException.__init__(self,*args,**kargs)

class SessionNotFoundException(CoordinatorServerException):
    def __init__(self, *args, **kargs):
        CoordinatorServerException.__init__(self,*args,**kargs)

class CouldNotCreateSessionException(CoordinatorServerException):
    def __init__(self, msg, exc, *args, **kargs):
        CoordinatorServerException.__init__(self,msg,exc,*args,**kargs)
        self.msg       = msg
        self.exception = exc
