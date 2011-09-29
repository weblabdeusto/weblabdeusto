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
import time
import unittest

import weblab.core.coordinator.status as WSS

from weblab.core.reservations import WaitingReservation, ConfirmedReservation, WaitingConfirmationReservation, WaitingInstances, PostReservationReservation, Reservation

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

    def test_translate_reservation_waiting_instances(self):
        status = WSS.WaitingInstancesQueueStatus('foo', 5)
        reservation = Reservation.translate_reservation(status)
        self.assertEquals(Reservation.WAITING_INSTANCES, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals(5, reservation.position)

    def test_translate_reservation_waiting(self):
        status = WSS.WaitingQueueStatus('foo', 5)
        reservation = Reservation.translate_reservation(status)
        self.assertEquals(Reservation.WAITING, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals(5, reservation.position)

    def test_translate_reservation_waiting_confirmation(self):
        status = WSS.WaitingConfirmationQueueStatus('foo', 'i:s@m', 100, 'http://...')
        reservation = Reservation.translate_reservation(status)
        self.assertEquals(Reservation.WAITING_CONFIRMATION, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals('http://...', reservation.url)

    def test_translate_reservation_reserved(self):
        status = WSS.ReservedStatus('foo', 'i:s@m', 'lab_session', 100, "{}", time.time(), time.time(), True, 80, 'http://...')
        reservation = Reservation.translate_reservation(status)
        self.assertEquals(Reservation.CONFIRMED, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals('http://...', reservation.url)
        self.assertEquals('{}', reservation.initial_configuration)

    def test_translate_reservation_post_reservation(self):
        status = WSS.PostReservationStatus('foo', True, "{ }", "{}")
        reservation = Reservation.translate_reservation(status)
        self.assertEquals(Reservation.POST_RESERVATION, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals('{ }', reservation.initial_data)
        self.assertEquals('{}', reservation.end_data)
        self.assertTrue(reservation.finished)

    def test_translate_reservation_from_data_waiting(self):
        reservation = Reservation.translate_reservation_from_data(Reservation.WAITING, 'foo', 5, None, None, None, None, None, None)
        self.assertEquals(Reservation.WAITING, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals(5, reservation.position)

    def test_translate_reservation_from_data_waiting_confirmation(self):
        reservation = Reservation.translate_reservation_from_data(Reservation.WAITING_CONFIRMATION, 'foo', None, None, None, None, 'http://...', None, None)
        self.assertEquals(Reservation.WAITING_CONFIRMATION, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals('http://...', reservation.url)

    def test_translate_reservation_from_data_waiting_instances(self):
        reservation = Reservation.translate_reservation_from_data(Reservation.WAITING_INSTANCES, 'foo', 5, None, None, None, None, None, None)
        self.assertEquals(Reservation.WAITING_INSTANCES, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals(5, reservation.position)

    def test_translate_reservation_from_data_confirmed(self):
        reservation = Reservation.translate_reservation_from_data(Reservation.CONFIRMED, 'foo', None, 80, "{}", None, 'http://...', None, None)
        self.assertEquals(Reservation.CONFIRMED, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals('http://...', reservation.url)
        self.assertEquals('{}', reservation.initial_configuration)

    def test_translate_reservation_from_data_post_reservation(self):
        reservation = Reservation.translate_reservation_from_data(Reservation.POST_RESERVATION, 'foo', None, None, None, "{}", None, True, "{ }")
        self.assertEquals(Reservation.POST_RESERVATION, reservation.status)
        self.assertEquals('foo', reservation.reservation_id.id)
        self.assertEquals('{ }', reservation.initial_data)
        self.assertEquals('{}', reservation.end_data)
        self.assertTrue(reservation.finished)



def suite():
    return unittest.makeSuite(ReservationTest)

if __name__ == '__main__':
    unittest.main()

