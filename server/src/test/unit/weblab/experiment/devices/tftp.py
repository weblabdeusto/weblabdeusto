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

from mock import patch
import unittest

from weblab.experiment.devices.tftp import TFtpDevice
import weblab.exceptions.experiment.devices.tftp_device.WlTFtpDeviceExceptions as WlTFtpDeviceExceptions


class TFtpDeviceTestCase(unittest.TestCase):

    def setUp(self):
        self.device = TFtpDevice("localhost", 69)

    @patch('subprocess.Popen')
    def test_put_ok(self, Popen):
        self.device.put("any command")

    @patch('subprocess.Popen')
    def test_put_create_popen_fail_value_error(self, Popen):
        Popen.side_effect = Exception('some error...')
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceCallingProcessException,
            self.device.put,
            "any command"
        )

    @patch('subprocess.Popen')
    def test_put_create_popen_fail_wait(self, Popen):
        popen = Popen.return_value
        popen.wait.side_effect = Exception('some error...')
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceWaitingCommandException,
            self.device.put,
            "any command"
        )

    @patch('subprocess.Popen')
    def test_put_create_popen_fail_reading_stdout(self, Popen):
        popen = Popen.return_value
        popen.stdout.read.side_effect = Exception('some error...')
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceRetrievingOutputFromCommandException,
            self.device.put,
            "any command"
        )

    @patch('subprocess.Popen')
    def test_put_create_popen_fail_reading_stderr(self, Popen):
        popen = Popen.return_value
        popen.stderr.read.side_effect = Exception('some error...')
        self.assertRaises(
            WlTFtpDeviceExceptions.WlTFtpDeviceRetrievingOutputFromCommandException,
            self.device.put,
            "any command"
        )


def suite():
    return unittest.makeSuite(TFtpDeviceTestCase)

if __name__ == '__main__':
    unittest.main()
