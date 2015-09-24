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
from __future__ import print_function, unicode_literals

import voodoo.exc as VoodooErrors

class SessionError(VoodooErrors.VoodooError):
    def __init__(self,*args,**kargs):
        VoodooErrors.VoodooError.__init__(self,*args,**kargs)

class SessionNotFoundError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionDatabaseExecutionError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionNotSerializableError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionNotDeserializableError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionSerializationNotImplementedError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionInvalidSessionIdError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionInvalidSessionTypeError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionTypeNotImplementedError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class VariableNotFoundInSessionError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class CouldntReleaseSessionError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class SessionAlreadyAcquiredError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)

class DesiredSessionIdAlreadyExistsError(SessionError):
    def __init__(self,*args,**kargs):
        SessionError.__init__(self,*args,**kargs)
