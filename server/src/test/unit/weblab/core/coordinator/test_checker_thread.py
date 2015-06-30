#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

import unittest
import time

import weblab.core.coordinator.checker_threaded as RCT
import weblab.core.coordinator.checker as ResourcesChecker

class Coordinator(object):
    locator = ""

original_coordinator = Coordinator()
counter = None
right_coordinator = None
checked = None

def initialize():
    global counter, right_coordinator, checked
    counter = 0
    right_coordinator = False
    checked = False

class FakeChecker(object):
    def __init__(self, coordinator):
        global counter, right_coordinator
        counter += 1
        if coordinator == original_coordinator:
            right_coordinator = True

    def check(self):
        global checked
        checked = True

class FakeFailingChecker(object):
    def __init__(self, coordinator):
        global counter, right_coordinator
        counter += 1
        if coordinator == original_coordinator:
            right_coordinator = True

    def check(self):
        global checked
        checked = True
        raise Exception("")

class ResourcesCheckerThreadTestCase(unittest.TestCase):
    def setUp(self):
        initialize()
        self.assertTrue(hasattr(ResourcesChecker.ResourcesChecker, 'check'))
        self.assertTrue(hasattr(FakeChecker, 'check'))
        self.assertTrue(hasattr(FakeFailingChecker, 'check'))

    def test_checking_not_failing(self):
        OriginalChecker = RCT.ResourcesCheckerThread.Checker
        RCT.ResourcesCheckerThread.Checker = FakeChecker
        original_sleep = RCT.sleep
        RCT.sleep = lambda *args : None
        try:
            RCT.reset()
            try:
                RCT.set_coordinator(original_coordinator, 10)
                time.sleep(0.01)
                self.assertTrue(counter > 2)
                self.assertTrue(right_coordinator)
                self.assertTrue(checked)
            finally:
                RCT.clean()
        finally:
            RCT.ResourcesCheckerThread.Checker = OriginalChecker
            RCT.sleep = original_sleep

    def test_checking_failing(self):
        OriginalChecker = RCT.ResourcesCheckerThread.Checker
        RCT.ResourcesCheckerThread.Checker = FakeFailingChecker
        original_sleep = RCT.sleep
        RCT.sleep = lambda *args : None
        try:
            RCT.reset()
            try:
                RCT.set_coordinator(original_coordinator, 10)
                initial_time = time.time()
                while not RCT.checker_thread.isAlive() and time.time() - initial_time <= 1:
                    time.sleep(0.02)
                # Now it's alive or more than 1 seconds have passed
                time.sleep(0.2)
                self.assertTrue(counter > 2) # It's still running
                self.assertTrue(right_coordinator)
                self.assertTrue(checked)
            finally:
                RCT.clean()
        finally:
            RCT.ResourcesCheckerThread.Checker = OriginalChecker
            RCT.sleep = original_sleep

def suite():
    return unittest.makeSuite(ResourcesCheckerThreadTestCase)

if __name__ == '__main__':
    unittest.main()

