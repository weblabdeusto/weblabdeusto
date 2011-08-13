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

import weblab.exceptions.experiment.devices.tftp_device.WlTFtpDeviceExceptions as WlTFtpDeviceExceptions
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
        except Exception, e:
            raise WlTFtpDeviceExceptions.WlTFtpDeviceCallingProcessException(e)
        popen.stdin.write('binary\n' + command + '\n')
        popen.stdin.close()
        try:
            result = popen.wait()
        except Exception, e:
            raise WlTFtpDeviceExceptions.WlTFtpDeviceWaitingCommandException(e)
        try:
            stdout_result = popen.stdout.read()
            stderr_result = popen.stderr.read()
        except Exception, e:
            raise WlTFtpDeviceExceptions.WlTFtpDeviceRetrievingOutputFromCommandException(e)
        return result, stdout_result, stderr_result
