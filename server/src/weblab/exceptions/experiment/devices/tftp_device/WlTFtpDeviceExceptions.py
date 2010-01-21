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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 
 
import weblab.exceptions.experiment.devices.DeviceExceptions as DeviceExceptions

class WlTFtpDeviceException(DeviceExceptions.DeviceException):
    def __init__(self, msg):
        DeviceExceptions.DeviceException.__init__(self, "Exception related to Weblab's TFtp device: %s" % msg)

class WlTFtpDeviceCallingProcessException(WlTFtpDeviceException):
    def __init__(self, e):
        WlTFtpDeviceException.__init__(self, "Failed calling tftp process: %s" % str(e))

class WlTFtpDeviceWaitingCommandException(WlTFtpDeviceException):
    def __init__(self, e):
        WlTFtpDeviceException.__init__(self, "An error ocurred while waiting for tftp command response: %s" % str(e) )

class WlTFtpDeviceRetrievingOutputFromCommandException(WlTFtpDeviceException):
    def __init__(self, msg):
        WlTFtpDeviceException.__init__(self, msg)

