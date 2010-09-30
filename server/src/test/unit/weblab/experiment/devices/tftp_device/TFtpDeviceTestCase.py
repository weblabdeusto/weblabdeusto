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

import unittest
import mocker

from weblab.experiment.devices.tftp_device.TFtpDevice import TFtpDevice
import weblab.exceptions.experiment.devices.tftp_device.WlTFtpDeviceExceptions as WlTFtpDeviceExceptions
        
        
class LierTFtpDevice(TFtpDevice):
    def __init__(self, mocked_popen, *args, **kargs):
        super(LierTFtpDevice, self).__init__(*args, **kargs)
        self.exceptionToRaise = None
        self.mocked_popen     = mocked_popen
        
    def force_raise(self, exceptionClass):
        self.exceptionToRaise = exceptionClass

    def _create_popen(self, cmd_file):
        if self.exceptionToRaise is not None:
            raise self.exceptionToRaise
        else:
            return self.mocked_popen

class TFtpDeviceTestCase(mocker.MockerTestCase):
    
    def setUp(self):
        self.mocked_popen = self.mocker.mock()
        self.device = LierTFtpDevice(self.mocked_popen, "localhost", 69)

    def test_put_ok(self):
        self.mocked_popen.stdin.write("binary\nany command\n")
        self.mocked_popen.stdin.close()
        self.mocked_popen.wait()
        self.mocked_popen.stdout.read()
        self.mocked_popen.stderr.read()

        self.mocker.replay()
        self.device.put("any command")
            
    def test_put_create_popen_fail_value_error(self):
        self.device.force_raise(Exception("some error..."))
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceCallingProcessException,
            self.device.put,
            "any command"
        )

    def test_put_create_popen_fail_wait(self):
        self.mocked_popen.stdin.write("binary\nany command\n")
        self.mocked_popen.stdin.close()
        self.mocked_popen.wait()
        self.mocker.throw(Exception("some error..."))

        self.mocker.replay()
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceWaitingCommandException,
            self.device.put,
            "any command"
        )

    def test_put_create_popen_fail_reading_output(self):
        self.mocked_popen.stdin.write("binary\nany command\n")
        self.mocked_popen.stdin.close()
        self.mocked_popen.wait()
        self.mocked_popen.stdout.read()
        self.mocker.throw(Exception("some error..."))

        self.mocker.replay()
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceRetrievingOutputFromCommandException,
            self.device.put,
            "any command"
        )
            
        
def suite():
    return unittest.makeSuite(TFtpDeviceTestCase)

if __name__ == '__main__':
    unittest.main()
