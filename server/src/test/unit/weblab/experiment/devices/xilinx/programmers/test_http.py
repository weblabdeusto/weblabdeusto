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

from mock import patch
import unittest
import urllib2

from weblab.experiment.devices.http import HttpDevice, WlHttpDeviceURLErrorError, WlHttpDeviceHTTPErrorError, WlHttpDeviceError
from test.util.fakeobjects import fakeaddinfourl


class HttpDeviceTestCase(unittest.TestCase):

    @patch('urllib2.urlopen')
    def test_ok_response(self, urlopen):
        urlopen.return_value = fakeaddinfourl('OK')

        device = HttpDevice("localhost", 7779)
        resp = device.send_message("command")
        self.assertEquals('OK', resp)

    @patch('urllib2.urlopen')
    def test_http_error_response(self, urlopen):
        urlopen.side_effect = urllib2.HTTPError('', 401, '', {}, None)

        device = HttpDevice("localhost", 7779)
        self.assertRaises(
            WlHttpDeviceHTTPErrorError,
            device.send_message,
            "command"
        )

    @patch('urllib2.urlopen')
    def test_url_error_response(self, urlopen):
        urlopen.side_effect = urllib2.URLError('error message')

        device = HttpDevice("localhost", 7779)
        self.assertRaises(
            WlHttpDeviceURLErrorError,
            device.send_message,
            "command"
        )

    @patch('urllib2.urlopen')
    def test_general_error_response(self, urlopen):
        urlopen.side_effect = Exception('error message')

        device = HttpDevice("localhost", 7779)
        self.assertRaises(
            WlHttpDeviceError,
            device.send_message,
            "command"
        )


def suite():
    return unittest.makeSuite(HttpDeviceTestCase)

if __name__ == '__main__':
    unittest.main()
