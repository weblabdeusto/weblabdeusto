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
import weblab.exceptions.WebLabExceptions as WebLabExceptions

class LaboratoryException(WebLabExceptions.WebLabException):
    def __init__(self,*args,**kargs):
        WebLabExceptions.WebLabException.__init__(self,*args,**kargs)

class ExperimentNotFoundException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class ExperimentAlreadyFoundException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class BusyExperimentException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class AlreadyFreedExperimentException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class FailedToSendFileException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class FailedToSendCommandException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class SessionNotFoundInLaboratoryServerException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class NotASessionTypeException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class InvalidLaboratoryConfigurationException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class CheckingHandlerException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class WebcamIsReturningAnImageHandlerException(CheckingHandlerException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class ImageURLDidNotRetrieveAResponseException(WebcamIsReturningAnImageHandlerException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class InvalidContentTypeRetrievedFromImageURLException(WebcamIsReturningAnImageHandlerException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)

class UnableToConnectHostnameInPortException(CheckingHandlerException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)
        
class ExperimentIsUpAndRunningErrorException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)
        
class InvalidIsUpAndRunningResponseFormatException(LaboratoryException):
    def __init__(self, *args, **kargs):
        LaboratoryException.__init__(self,*args,**kargs)