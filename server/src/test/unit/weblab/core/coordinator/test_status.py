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

class WebLabSchedulingStatusTest(unittest.TestCase):

    def test_str_waiting_instances(self):
        wi = WSS.WaitingInstancesQueueStatus("reservation_id", 5)
        str(wi)

    def test_str_waiting(self):
        w = WSS.WaitingQueueStatus("reservation_id", 4)
        str(w)

    def test_str_waiting_confirmation(self):
        wc     = WSS.WaitingConfirmationQueueStatus("reservation_id", 'http://www.weblab.deusto.es/weblab/client/...')
        str(wc)

    def test_str_local_reservation(self):
        res    = WSS.LocalReservedStatus("reservation_id", "coord_address1", "lab_session_id1", {}, 50, None, datetime.datetime.now(), datetime.datetime.now(), True, 45, 'http://www.weblab.deusto.es/weblab/client/#reservation-id=foo&...')
        str(res)

    def test_str_remote_reservation(self):
        res    = WSS.RemoteReservedStatus("reservation_id", 50, '{}', 'http://www.weblab.deusto.es/weblab/client/#reservation-id=foo&...', 'remote_reservation_id')
        str(res)

    def test_str_post_reservation(self):
        post   = WSS.PostReservationStatus("reservation_id", True, "foo1", "bar")
        str(post)

def suite():
    return unittest.makeSuite(WebLabSchedulingStatusTest)

if __name__ == '__main__':
    unittest.main()

