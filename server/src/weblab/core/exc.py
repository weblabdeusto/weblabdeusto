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
    pass

#
# from UserProcessingException
#

class SessionNotFoundException(UserProcessingException):
    pass

class NoCurrentReservationException(UserProcessingException):
    pass

class FailedToInteractException(UserProcessingException):
    pass

class FailedToSendFileException(FailedToInteractException):
    pass

class FailedToSendCommandException(FailedToInteractException):
    pass

class FailedToFreeReservationException(UserProcessingException):
    pass

class CoordinationConfigurationParsingException(UserProcessingException):
    pass

class ReservationFailedException(UserProcessingException):
    pass

#
# from ReservationFailedException
#

class UnknownExperimentIdException(ReservationFailedException):
    pass

class NoAvailableExperimentFoundException(ReservationFailedException):
    pass

class InvalidReservationStatusException(ReservationFailedException):
    pass

class NotASessionTypeException(ReservationFailedException):
    pass

