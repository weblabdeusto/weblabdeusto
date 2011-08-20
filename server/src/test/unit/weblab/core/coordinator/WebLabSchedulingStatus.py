#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import datetime
import unittest

import weblab.core.coordinator.WebLabSchedulingStatus as WSS

class WebLabSchedulingStatusTest(unittest.TestCase):

    def test_str_waiting_instances(self):
        wi = WSS.WaitingInstancesQueueStatus(5)
        str(wi)

    def test_str_waiting(self):
        w = WSS.WaitingQueueStatus(4)
        str(w)

    def test_str_waiting_confirmation(self):
        wc     = WSS.WaitingConfirmationQueueStatus("coord_adress1", 50)
        str(wc)

    def test_str_reservation(self):
        res    = WSS.ReservedStatus("coord_address1", "lab_session_id1", 50, None, datetime.datetime.now(), datetime.datetime.now())
        str(res)

    def test_str_post_reservation(self):
        post   = WSS.PostReservationStatus(True, "foo1", "bar")
        str(post)

def suite():
    return unittest.makeSuite(WebLabSchedulingStatusTest)

if __name__ == '__main__':
    unittest.main()

