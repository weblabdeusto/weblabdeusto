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
# Author: Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

import time
import unittest
from voodoo.threaded import threaded
import weblab.core.coordinator.scheduler_transactions_synchronizer as scheduler_transactions_synchronizer
import test.util.module_disposer as module_disposer

class FakeScheduler(object):
    def __init__(self):
        self.updates = 0
        self.time_to_sleep = 0
    def update(self):
        time.sleep(self.time_to_sleep)
        self.updates += 1

@module_disposer.case_uses_module(scheduler_transactions_synchronizer)
class SchedulerTransactionsSynchronizerTestCase(unittest.TestCase):
    def setUp(self):
        self.scheduler = FakeScheduler()
        self.synchronizer = scheduler_transactions_synchronizer.SchedulerTransactionsSynchronizer(self.scheduler)
        self.synchronizer.start()
        self.requests = 0

    def test_updates(self):
        self.assertEquals(0, self.scheduler.updates)

        self.synchronizer.request_and_wait()

        self.assertEquals(1, self.scheduler.updates)

        self.synchronizer.request_and_wait()

        self.assertEquals(2, self.scheduler.updates)

    @threaded()
    def _request_threaded(self):
        self.requests += 1
        self.synchronizer.request_and_wait()

    def test_concurrent_updates(self):
        self.scheduler.time_to_sleep = 0.2

        self.assertEquals(0, self.scheduler.updates)

        t_initial = self._request_threaded()

        # Wait for it to be initialized
        while self.requests == 0:
            time.sleep(0.001)

        time.sleep(0.05)

        # At this point, it's in the middle of a update
        # Let's send 6 more requests
        t1 = self._request_threaded()
        t2 = self._request_threaded()
        t3 = self._request_threaded()
        t4 = self._request_threaded()
        t5 = self._request_threaded()
        t6 = self._request_threaded()

        # Wait for the first one
        t_initial.join()
        self.assertEquals(1, self.scheduler.updates)

        # Wait for the rest
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()

        # Check that there was a single, shared update
        self.assertEquals(2, self.scheduler.updates)

    def tearDown(self):
        self.synchronizer.stop()

def suite():
    return unittest.makeSuite(SchedulerTransactionsSynchronizerTestCase)

if __name__ == '__main__':
    unittest.main()

