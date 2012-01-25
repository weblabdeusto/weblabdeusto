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

class WebLabCoreException(wlExc.WebLabException):
    pass

#
# from WebLabCoreException
#

class SessionNotFoundException(WebLabCoreException):
    pass

class NoCurrentReservationException(WebLabCoreException):
    pass

class FailedToInteractException(WebLabCoreException):
    pass

class FailedToSendFileException(FailedToInteractException):
    pass

class FailedToSendCommandException(FailedToInteractException):
    pass

class FailedToFreeReservationException(WebLabCoreException):
    pass

class CoordinationConfigurationParsingException(WebLabCoreException):
    pass

class ReservationFailedException(WebLabCoreException):
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

