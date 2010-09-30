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

from __future__ import with_statement

import unittest
import urllib2
from mocker import Mocker

from test.unit.weblab.experiment.devices.http_device.FakeHttpServer import FakeHttpServer
from weblab.experiment.devices.http_device.HttpDevice import HttpDevice
import weblab.exceptions.experiment.devices.http_device.WlHttpDeviceExceptions as WlHttpDeviceExceptions

class MockedHttpDevice(HttpDevice):
    def __init__(self, urlmodule, *args, **kargs):
        self.__urlmodule = urlmodule
        super(MockedHttpDevice, self).__init__(*args, **kargs)
        
    def _urlmodule(self):
        return self.__urlmodule

class HttpDeviceTestCase(unittest.TestCase):
    
    def __init__(self, *args, **kargs):
        unittest.TestCase.__init__(self, *args, **kargs)
            
    def setUp(self):
        self.fake_http_server = FakeHttpServer(7779)
        self.fake_http_server.start()
        self.fake_http_server.wait_until_handling()
        self.real_device = HttpDevice("localhost", 7779)
        self.mocker = Mocker()
        self.urllib_mocked = self.mocker.mock()
        self.mocked_device = MockedHttpDevice(self.urllib_mocked, "localhost", 7779)

    def tearDown(self):
        self.fake_http_server.stop()
        self.fake_http_server.join()

    def test_ok_response(self):
        self.fake_http_server.set_answer(200)
        response = self.real_device.send_message("any command")
        self.assertEquals(FakeHttpServer.DEFAULT_RESPONSE, response)
        
    def test_http_error_response(self):
        self.fake_http_server.set_answer(401)
        self.assertRaises(
                WlHttpDeviceExceptions.WlHttpDeviceHTTPErrorException, 
                self.real_device.send_message, 
                "any command"
            )

    def test_url_error_response(self):
        self.urllib_mocked.urlopen('http://localhost:7779/', 'any command')
        self.mocker.throw(urllib2.URLError("error message"))
        
        with self.mocker:
            self.assertRaises(
                WlHttpDeviceExceptions.WlHttpDeviceURLErrorException,
                self.mocked_device.send_message,
                "any command"
            )
        
    def test_general_error_response(self):
        self.urllib_mocked.urlopen('http://localhost:7779/', 'any command')
        self.mocker.throw(Exception("error message"))
        
        with self.mocker:
            self.assertRaises(
                WlHttpDeviceExceptions.WlHttpDeviceException,
                self.mocked_device.send_message,
                "any command"
            )
        
        
def suite():
    return unittest.makeSuite(HttpDeviceTestCase)

if __name__ == '__main__':
    unittest.main()
