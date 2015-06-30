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

class LaboratoryError(wlExc.WebLabError):
    pass

class ExperimentNotFoundError(LaboratoryError):
    pass

class ExperimentAlreadyFoundError(LaboratoryError):
    pass

class BusyExperimentError(LaboratoryError):
    pass

class AlreadyFreedExperimentError(LaboratoryError):
    pass

class FailedToInteractError(LaboratoryError):
    pass

class FailedToSendFileError(FailedToInteractError):
    pass

class FailedToSendCommandError(FailedToInteractError):
    pass

class SessionNotFoundInLaboratoryServerError(LaboratoryError):
    pass

class NotASessionTypeError(LaboratoryError):
    pass

class InvalidLaboratoryConfigurationError(LaboratoryError):
    pass

class CheckingHandlerError(LaboratoryError):
    pass

class WebcamIsReturningAnImageHandlerError(CheckingHandlerError):
    pass

class ImageURLDidNotRetrieveAResponseError(WebcamIsReturningAnImageHandlerError):
    pass

class InvalidContentTypeRetrievedFromImageURLError(WebcamIsReturningAnImageHandlerError):
    pass

class UnableToConnectHostnameInPortError(CheckingHandlerError):
    pass

