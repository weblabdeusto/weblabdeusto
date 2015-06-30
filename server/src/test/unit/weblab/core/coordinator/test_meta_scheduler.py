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

import datetime
import unittest

import weblab.core.coordinator.status as WSS

class FakeScheduler(object):
    def __init__(self, reservation_status, expected_reservation_id):
        self.reservation_status      = reservation_status
        self.expected_reservation_id = expected_reservation_id

    def is_remote(self):
        return False

    def get_reservation_status(self, reservation_id):
        if reservation_id != self.expected_reservation_id:
            raise ValueError("Expected: %s; found %s" % (self.expected_reservation_id, reservation_id))
        return self.reservation_status


class MetaSchedulerTestCase(unittest.TestCase):
    def setUp(self):
        self.wi_five = WSS.WaitingInstancesQueueStatus("reservation_id", 5)
        self.wi_four = WSS.WaitingInstancesQueueStatus("reservation_id", 4)

        self.w_five  = WSS.WaitingQueueStatus("reservation_id", 5)
        self.w_four  = WSS.WaitingQueueStatus("reservation_id", 4)

        self.wc1     = WSS.WaitingConfirmationQueueStatus("reservation_id", 'http://www.weblab.deusto.es/weblab/client/...')
        self.wc2     = WSS.WaitingConfirmationQueueStatus("reservation_id", 'http://www.weblab.deusto.es/weblab/client/...')

        self.res1    = WSS.LocalReservedStatus("reservation_id", "coord_address1", "lab_session_id1", {}, 50, None, datetime.datetime.now(), datetime.datetime.now(), True, 50, 'http://www.weblab.deusto.es/weblab/client/foo')
        self.res2    = WSS.LocalReservedStatus("reservation_id", "coord_address2", "lab_session_id2", {}, 60, "foo", datetime.datetime.now(), datetime.datetime.now(), True, 50, 'http://www.weblab.deusto.es/weblab/client/foo')

        self.post1   = WSS.PostReservationStatus("reservation_id", True, "foo1", "bar")
        self.post2   = WSS.PostReservationStatus("reservation_id", True, "foo2", "bar")

    def test_query_best_reservation__waiting_instances_equals(self):
        "Among Waiting for instances, the lower number the better"
        self._test_schedulers(self.wi_four, (self.wi_four, self.wi_five))
        self._test_schedulers(self.wi_four, (self.wi_five, self.wi_four))

    def test_query_best_reservation__waiting_equals(self):
        "Among Waiting, the lower number the better"
        self._test_schedulers(self.w_four, (self.w_four, self.w_five))
        self._test_schedulers(self.w_four, (self.w_five, self.w_four))

    def test_query_best_reservation__waiting_confirmation_equals(self):
        "Among WaitingConfirmation, they're all the same"
        self._test_schedulers((self.wc1, self.wc2), (self.wc1, self.wc2))
        self._test_schedulers((self.wc1, self.wc2), (self.wc2, self.wc1))

    def test_query_best_reservation__reserved_equals(self):
        "Among LocalReservedStatus, they're all the same"
        self._test_schedulers((self.res1, self.res2), (self.res1, self.res2))
        self._test_schedulers((self.res1, self.res2), (self.res2, self.res1))

    def test_query_best_reservation__post_reservation_equals(self):
        "Among PostReservationStatus, they're all the same"
        self._test_schedulers((self.post1, self.post2), (self.post1, self.post2))
        self._test_schedulers((self.post1, self.post2), (self.post2, self.post1))

    def test_query_best_reservation__waiting_wins(self):
        "Waiting wins to WaitingInstances"
        self._test_schedulers(self.w_four, (self.w_four,  self.wi_four, self.wi_four))
        self._test_schedulers(self.w_four, (self.wi_four, self.w_four,  self.wi_five))
        self._test_schedulers(self.w_four, (self.wi_four, self.wi_five, self.w_four))

    def test_query_best_reservation__waiting_confirmation_wins(self):
        "WaitingConfirmation wins to Waiting and WaitingInstances"
        self._test_schedulers(self.wc1,    (self.wc1, self.w_four, self.wi_four, self.post1))
        self._test_schedulers(self.wc1,    (self.w_four, self.wc1, self.wi_four, self.post1))
        self._test_schedulers(self.wc1,    (self.w_four, self.wi_four, self.wc1, self.post1))

    def test_query_best_reservation__reserved_wins(self):
        "Reserved wins them all"
        self._test_schedulers(self.res1,   (self.res1, self.wc1, self.w_four, self.wi_four, self.post1))
        self._test_schedulers(self.res1,   (self.wc1, self.res1, self.w_four, self.wi_four, self.post1))
        self._test_schedulers(self.res1,   (self.wc1, self.w_four, self.res1, self.wi_four, self.post1))
        self._test_schedulers(self.res1,   (self.wc1, self.w_four, self.wi_four, self.res1, self.post1))

    def test_query_best_reservation__post_reservation_wins(self):
        "PostReservation wins them all"
        self._test_schedulers(self.post1,   (self.post1, self.w_four, self.wi_four))
        self._test_schedulers(self.post1,   (self.post1, self.w_four, self.wi_four))
        self._test_schedulers(self.post1,   (self.w_four, self.post1, self.wi_four))
        self._test_schedulers(self.post1,   (self.w_four, self.wi_four, self.post1 ))
        self._test_schedulers(self.post1,   (self.w_four, self.wi_four, self.post1))

    def _test_schedulers(self, best, all_status):
        best_reservation_status = sorted(all_status)[0]

        try:
            best[0]
        except TypeError:
            self.assertEquals(best, best_reservation_status)
        else:
            self.assertTrue(best_reservation_status in best)

def suite():
    return unittest.makeSuite(MetaSchedulerTestCase)

if __name__ == '__main__':
    unittest.main()

