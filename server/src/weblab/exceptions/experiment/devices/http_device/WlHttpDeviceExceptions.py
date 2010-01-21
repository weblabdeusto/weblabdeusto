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

class WlHttpDeviceException(DeviceExceptions.DeviceException):
    def __init__(self, msg):
        DeviceExceptions.DeviceException.__init__(self, "Exception related to Weblab's Http device: %s" % msg)
 
class WlHttpDeviceURLErrorException(WlHttpDeviceException):
    def __init__(self, e = None):
        text = "Failed reaching the server"
        if hasattr(e, "reason"):
            text += ": %(r)s" % {'r':e.reason}
        WlHttpDeviceException.__init__(self, text)

class WlHttpDeviceHTTPErrorException(WlHttpDeviceException):
    def __init__(self, e = None):
        text = "The server couldn't fulfill the request"
        if hasattr(e, "code"):
            text += ": %(c)i" % {'c':e.code}        
        else:
            text += ": %s" % e
        WlHttpDeviceException.__init__(self, text)
