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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import weblab.exceptions.experiment.devices.DeviceExceptions as DeviceExceptions

class CantFindJTagBlazerProperty(DeviceExceptions.MisconfiguredDeviceException):
    def __init__(self, *args, **kargs):
        DeviceExceptions.MisconfiguredDeviceException.__init__(self, *args, **kargs)

class AlreadyProgrammingDeviceException(DeviceExceptions.AlreadyProgrammingDeviceException):
    def __init__(self, *args, **kargs):
        DeviceExceptions.AlreadyProgrammingDeviceException.__init__(self, *args, **kargs)
        
class ErrorProgrammingDeviceException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)        
        
class JTagBlazerSvf2JsvfErrorException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)

class ErrorRetrievingOutputFromJTagBlazerSvf2JsvfException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)

class ErrorWaitingForJTagBlazerSvf2JsvfFinishedException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)

class JTagBlazerTargetErrorException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)

class ErrorRetrievingOutputFromJTagBlazerTargetException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)

class ErrorWaitingForJTagBlazerTargetFinishedException(DeviceExceptions.ProgrammingDeviceException):
    def __init__(self,*args,**kargs):
        DeviceExceptions.ProgrammingDeviceException.__init__(self,*args,**kargs)

class InvalidSvfFileExtException(DeviceExceptions.DeviceException):
    def __init__(self, *args, **kargs):
        DeviceExceptions.DeviceException.__init__(self, *args, **kargs)
