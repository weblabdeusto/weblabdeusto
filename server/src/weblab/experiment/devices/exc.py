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

import weblab.experiment.exc as ExperimentExceptions

class DeviceException(ExperimentExceptions.ExperimentException):
    def __init__(self,*args,**kargs):
        ExperimentExceptions.ExperimentException.__init__(self,*args,**kargs)

class MisconfiguredDeviceException(DeviceException):
    def __init__(self, *args, **kargs):
        DeviceException.__init__(self, *args, **kargs)

class AlreadyProgrammingDeviceException(DeviceException):
    def __init__(self, *args, **kargs):
        DeviceException.__init__(self, *args, **kargs)

class ProgrammingDeviceException(DeviceException):
    def __init__(self, *args, **kargs):
        DeviceException.__init__(self, *args, **kargs)

