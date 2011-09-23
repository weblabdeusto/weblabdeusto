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

from weblab.core.reservations import WaitingReservation, ConfirmedReservation, WaitingConfirmationReservation, WaitingInstances, PostReservationReservation

class ReservationTest(unittest.TestCase):

    def assertCorrectReservation(self, reservation):
        self.assertEquals(str(reservation), str(eval(str(reservation))))

    def test_str_waiting_reservation(self):
        reservation = WaitingReservation("reservation_id", 5)
        self.assertCorrectReservation(reservation)

    def test_str_waiting_instances_reservation(self):
        reservation = WaitingInstances("reservation_id", 5)
        self.assertCorrectReservation(reservation)
        
    def test_str_confirmed_reservation(self):
        reservation = ConfirmedReservation("reservation_id", datetime.datetime.now(), "{}", 'http://www.weblab.deusto.es/...')
        self.assertCorrectReservation(reservation)

    def test_str_waiting_confirmation_reservation(self):
        reservation = WaitingConfirmationReservation("reservation_id", 'http://www.weblab.deusto.es/...')
        self.assertCorrectReservation(reservation)

    def test_str_post_reservation_reservation(self):
        reservation = PostReservationReservation("reservation_id", True, "{}", '{"foo"="bar"}')
        self.assertCorrectReservation(reservation)

def suite():
    return unittest.makeSuite(ReservationTest)

if __name__ == '__main__':
    unittest.main()

