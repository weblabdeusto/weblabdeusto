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
import weblab.exc as wlExc

#
# from WebLabError
#

class WebLabCoreError(wlExc.WebLabError):
    pass

#
# from WebLabCoreError
#

class SessionNotFoundError(WebLabCoreError):
    pass

class NoCurrentReservationError(WebLabCoreError):
    pass

class FailedToInteractError(WebLabCoreError):
    pass

class FailedToSendFileError(FailedToInteractError):
    pass

class FailedToSendCommandError(FailedToInteractError):
    pass

class FailedToFreeReservationError(WebLabCoreError):
    pass

class CoordinationConfigurationParsingError(WebLabCoreError):
    pass

class ReservationFailedError(WebLabCoreError):
    pass

#
# from ReservationFailedError
#

class UnknownExperimentIdError(ReservationFailedError):
    pass

class NoAvailableExperimentFoundError(ReservationFailedError):
    pass

class InvalidReservationStatusError(ReservationFailedError):
    pass

class NotASessionTypeError(ReservationFailedError):
    pass



#
# from DbErrors
# 
class DatabaseError(wlExc.WebLabError):
    def __init__(self,*args,**kargs):
        wlExc.WebLabError.__init__(self,*args,**kargs)

class DbInvalidUserOrPasswordError(DatabaseError):
    def __init__(self,*args,**kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbUserNotFoundError(DbInvalidUserOrPasswordError):
    def __init__(self,*args,**kargs):
        DbInvalidUserOrPasswordError.__init__(self,*args,**kargs)

class DbInvitationNotFoundError(DatabaseError):
    def __init__(self,*args,**kwargs):
        DatabaseError.__init__(*args,**kwargs)

class DbGroupNotFoundError(DatabaseError):
    def __init__(self,*args,**kwargs):
        DatabaseError.__init__(*args,**kwargs)

class DbProvidedUserNotFoundError(DatabaseError):
    def __init__(self,*args,**kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbHashAlgorithmNotFoundError(DatabaseError):
    def __init__(self,*args,**kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbInvalidPasswordFormatError(DatabaseError):
    def __init__(self,*args,**kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbIllegalStatusError(DatabaseError):
    def __init__(self,*args,**kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbMisconfiguredError(DatabaseError):
    def __init__(self, *args, **kargs):
        DatabaseError.__init__(self,*args,**kargs)

class InvalidPermissionParameterFormatError(DatabaseError):
    def __init__(self, *args, **kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbProvidedExperimentNotFoundError(DatabaseError):
    def __init__(self, *args, **kargs):
        DatabaseError.__init__(self,*args,**kargs)

class DbUserAuthError(DatabaseError):
    def __init__(self, *args, **kargs):
        DatabaseError.__init__(self, *args, **kargs)

class DbUnsupportedUserAuth(DbUserAuthError):
    def __init__(self, *args, **kargs):
        DbUserAuthError.__init__(self, *args, **kargs)

class DbInvalidUserAuthConfigurationError(DbUserAuthError):
    def __init__(self, *args, **kargs):
        DbUserAuthError.__init__(self, *args, **kargs)

class DbNoUserAuthNorPasswordFoundError(DbUserAuthError):
    def __init__(self, *args, **kargs):
        DbUserAuthError.__init__(self, *args, **kargs)

