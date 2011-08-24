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

import voodoo.exc as VoodooExceptions

class SessionException(VoodooExceptions.VoodooException):
    def __init__(self,*args,**kargs):
        VoodooExceptions.VoodooException.__init__(self,*args,**kargs)

class SessionNotFoundException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionDatabaseConnectionException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionDatabaseExecutionException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionNotSerializableException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionNotDeserializableException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionSerializationNotImplementedException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionInvalidSessionIdException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionInvalidSessionTypeException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionTypeNotImplementedException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class VariableNotFoundInSessionException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class CouldntAcquireSessionException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class CouldntReleaseSessionException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class SessionAlreadyAcquiredException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)

class DesiredSessionIdAlreadyExistsException(SessionException):
    def __init__(self,*args,**kargs):
        SessionException.__init__(self,*args,**kargs)
