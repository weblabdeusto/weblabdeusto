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

import unittest

from weblab.lab.status_handler import WebcamIsUpAndRunningHandler, HostIsUpAndRunningHandler, AbstractLightweightIsUpAndRunningHandler
import weblab.lab.exc as LaboratoryErrors
import test.unit.weblab.lab.fake_urllib2 as FakeUrllib2
import test.unit.weblab.lab.fake_socket as FakeSocket


class AbstractLightweightIsUpAndRunningHandlerTestCase(unittest.TestCase):

    def test_not_implemented(self):
        self.assertRaises(
            TypeError,
            AbstractLightweightIsUpAndRunningHandler
        )


class WebcamIsUpAndRunningHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.handler = WebcamIsUpAndRunningHandler("https://...")
        FakeUrllib2.reset()
        self.handler._urllib2 = FakeUrllib2

    def test_run_ok(self):
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_OK
        self.handler.run()

    def test_run_exception_bad_response(self):
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_URL_ERROR
        self.assertRaises(
            LaboratoryErrors.ImageURLDidNotRetrieveAResponseError,
            self.handler.run
        )

    def test_run_exception_bad_content(self):
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_BAD_CONTENT
        self.assertRaises(
            LaboratoryErrors.InvalidContentTypeRetrievedFromImageURLError,
            self.handler.run
        )

    def test_run_times(self):
        messages = self.handler.run_times()
        self.assertEquals([], messages)
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_BAD_CONTENT
        messages = self.handler.run_times()
        self.assertEquals(WebcamIsUpAndRunningHandler.DEFAULT_TIMES, len(messages))


class HostIsUpAndRunningHandlerTestCase(unittest.TestCase):

    def setUp(self):
        FakeSocket.reset()
        self.handler = HostIsUpAndRunningHandler("hostname", 80)
        self.handler._socket = FakeSocket

    def test_run_ok(self):
        FakeSocket.expected_action = FakeSocket.OK
        self.handler.run()

    def test_run_error(self):
        FakeSocket.expected_action = FakeSocket.ERROR
        self.assertRaises(
            LaboratoryErrors.UnableToConnectHostnameInPortError,
            self.handler.run
        )


def suite():
    return unittest.TestSuite(
            (
                unittest.makeSuite(AbstractLightweightIsUpAndRunningHandlerTestCase),
                unittest.makeSuite(WebcamIsUpAndRunningHandlerTestCase),
                unittest.makeSuite(HostIsUpAndRunningHandlerTestCase),
            )
        )


if __name__ == '__main__':
    unittest.main()
