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
import weblab.exc as wlExc

#
# from WebLabException
#

class UserProcessingException(wlExc.WebLabException):
    def __init__(self,*args,**kargs):
        wlExc.WebLabException.__init__(self,*args,**kargs)

#
# from UserProcessingException
#

class SessionNotFoundException(UserProcessingException):
    def __init__(self,*args,**kargs):
        UserProcessingException.__init__(self,*args,**kargs)

class NoCurrentReservationException(UserProcessingException):
    def __init__(self, *args, **kargs):
        UserProcessingException.__init__(self, *args, **kargs)

class FailedToSendFileException(UserProcessingException):
    def __init__(self, *args, **kargs):
        UserProcessingException.__init__(self, *args, **kargs)

class FailedToSendCommandException(UserProcessingException):
    def __init__(self, *args, **kargs):
        UserProcessingException.__init__(self, *args, **kargs)

class FailedToFreeReservationException(UserProcessingException):
    def __init__(self, *args, **kargs):
        UserProcessingException.__init__(self, *args, **kargs)

class CoordinationConfigurationParsingException(UserProcessingException):
    def __init__(self,*args,**kargs):
        UserProcessingException.__init__(self,*args,**kargs)

class ReservationFailedException(UserProcessingException):
    def __init__(self,*args,**kargs):
        UserProcessingException.__init__(self,*args,**kargs)

#
# from ReservationFailedException
#

class UnknownExperimentIdException(ReservationFailedException):
    def __init__(self,*args,**kargs):
        ReservationFailedException.__init__(self,*args,**kargs)

class NoAvailableExperimentFoundException(ReservationFailedException):
    def __init__(self,*args,**kargs):
        ReservationFailedException.__init__(self,*args,**kargs)

class InvalidReservationStatusException(ReservationFailedException):
    def __init__(self,*args,**kargs):
        ReservationFailedException.__init__(self,*args,**kargs)

class NotASessionTypeException(ReservationFailedException):
    def __init__(self,*args,**kargs):
        ReservationFailedException.__init__(self,*args,**kargs)
