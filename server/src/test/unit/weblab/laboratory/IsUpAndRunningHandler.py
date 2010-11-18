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

from weblab.laboratory.IsUpAndRunningHandler import WebcamIsUpAndRunningHandler, HostIsUpAndRunningHandler, AbstractIsUpAndRunningHandler
import weblab.exceptions.laboratory.LaboratoryExceptions as LaboratoryExceptions
import FakeUrllib2
import FakeSocket


class AbstractIsUpAndRunningHandlerTestCase(unittest.TestCase):
    
    def test(self):
        h = AbstractIsUpAndRunningHandler()
        self.assertRaises(
            NotImplementedError,
            h.run
        )


class WebcamIsUpAndRunningHandlerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.handler = WebcamIsUpAndRunningHandler("https://...")
        self.handler._urllib2 = FakeUrllib2
    
    def test_run_ok(self):
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_OK
        self.handler.run()
        
    def test_run_exception_bad_response(self):
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_URL_ERROR
        self.assertRaises(
            LaboratoryExceptions.ImageURLDidNotRetrieveAResponseException,
            self.handler.run
        )
        
    def test_run_exception_bad_content(self):
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_BAD_CONTENT
        self.assertRaises(
            LaboratoryExceptions.InvalidContentTypeRetrievedFromImageURLException,
            self.handler.run
        )
        

class HostIsUpAndRunningHandlerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.handler = HostIsUpAndRunningHandler("hostname", 80)
        self.handler._socket = FakeSocket
    
    def test_run_ok(self):
        FakeSocket.expected_action = FakeSocket.OK
        self.handler.run()
        
    def test_run_error(self):
        FakeSocket.expected_action = FakeSocket.ERROR
        self.assertRaises(
            LaboratoryExceptions.UnableToConnectHostnameInPortException,
            self.handler.run
        )
        

def suite():
    return unittest.TestSuite(
            (
                unittest.makeSuite(AbstractIsUpAndRunningHandlerTestCase),
                unittest.makeSuite(WebcamIsUpAndRunningHandlerTestCase),
                unittest.makeSuite(HostIsUpAndRunningHandlerTestCase),
            )
        )


if __name__ == '__main__':
    unittest.main()
