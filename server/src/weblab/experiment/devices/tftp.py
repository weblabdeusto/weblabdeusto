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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import weblab.experiment.devices.exc as DeviceErrors
import subprocess

class TFtpDevice(object):

    def __init__(self, hostname, port=69):
        super(TFtpDevice,self).__init__()
        self.hostname = hostname
        self.port     = port

    def put(self, command):
        try:
            popen = subprocess.Popen(
                ['tftp', self.hostname, str(self.port)],
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
        except Exception as e:
            raise WlTFtpDeviceCallingProcessError(e)
        popen.stdin.write('binary\n' + command + '\n')
        popen.stdin.close()
        try:
            result = popen.wait()
        except Exception as e:
            raise WlTFtpDeviceWaitingCommandError(e)
        try:
            stdout_result = popen.stdout.read()
            stderr_result = popen.stderr.read()
        except Exception as e:
            raise WlTFtpDeviceRetrievingOutputFromCommandError(e)
        return result, stdout_result, stderr_result

class WlTFtpDeviceError(DeviceErrors.DeviceError):
    def __init__(self, msg):
        DeviceErrors.DeviceError.__init__(self, "Exception related to Weblab's TFtp device: %s" % msg)

class WlTFtpDeviceCallingProcessError(WlTFtpDeviceError):
    def __init__(self, e):
        WlTFtpDeviceError.__init__(self, "Failed calling tftp process: %s" % str(e))

class WlTFtpDeviceWaitingCommandError(WlTFtpDeviceError):
    def __init__(self, e):
        WlTFtpDeviceError.__init__(self, "An error ocurred while waiting for tftp command response: %s" % str(e) )

class WlTFtpDeviceRetrievingOutputFromCommandError(WlTFtpDeviceError):
    def __init__(self, msg):
        WlTFtpDeviceError.__init__(self, msg)

