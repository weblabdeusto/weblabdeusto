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
import weblab.exc as wlExc

class LaboratoryException(wlExc.WebLabException):
    pass

class ExperimentNotFoundException(LaboratoryException):
    pass

class ExperimentAlreadyFoundException(LaboratoryException):
    pass

class BusyExperimentException(LaboratoryException):
    pass

class AlreadyFreedExperimentException(LaboratoryException):
    pass

class FailedToInteractException(LaboratoryException):
    pass

class FailedToSendFileException(FailedToInteractException):
    pass

class FailedToSendCommandException(FailedToInteractException):
    pass

class SessionNotFoundInLaboratoryServerException(LaboratoryException):
    pass

class NotASessionTypeException(LaboratoryException):
    pass

class InvalidLaboratoryConfigurationException(LaboratoryException):
    pass

class CheckingHandlerException(LaboratoryException):
    pass

class WebcamIsReturningAnImageHandlerException(CheckingHandlerException):
    pass

class ImageURLDidNotRetrieveAResponseException(WebcamIsReturningAnImageHandlerException):
    pass

class InvalidContentTypeRetrievedFromImageURLException(WebcamIsReturningAnImageHandlerException):
    pass

class UnableToConnectHostnameInPortException(CheckingHandlerException):
    pass

