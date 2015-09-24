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

from abc import ABCMeta, abstractmethod

from voodoo.sessions.session_id import SessionId

import weblab.core.coordinator.status as WSS
from weblab.core.exc import InvalidReservationStatusError

NULL_POSITION = 100000

class Reservation(object):

    __metaclass__ = ABCMeta

    WAITING              = "Reservation::waiting"
    WAITING_CONFIRMATION = "Reservation::waiting_confirmation"
    WAITING_INSTANCES    = "Reservation::waiting_instances"
    CONFIRMED            = "Reservation::confirmed"
    POST_RESERVATION     = "Reservation::post_reservation"

    POLLING_STATUS = (WAITING, WAITING_CONFIRMATION, WAITING_INSTANCES, CONFIRMED)

    def __init__(self, status, reservation_id):
        """ __init__(status, reservation_id)

        status is Reservation.WAITING, Reservation.CONFIRMED, etc.
        reservation_id is the reservation identifier, used to interact with the experiment
        """
        super(Reservation,self).__init__()
        self.status         = status
        self.reservation_id = SessionId(reservation_id)

    def __repr__(self):
        return self.status

    @staticmethod
    def translate_reservation(status):
        if status.status == WSS.WebLabSchedulingStatus.WAITING:
            reservation = WaitingReservation(status.reservation_id, status.position)
        elif status.status == WSS.WebLabSchedulingStatus.WAITING_CONFIRMATION:
            reservation = WaitingConfirmationReservation(status.reservation_id, status.url)
        elif status.status == WSS.WebLabSchedulingStatus.RESERVED_REMOTE:
            reservation = ConfirmedReservation(status.reservation_id, status.remaining_time, status.initial_configuration, status.url, status.remote_reservation_id)
        elif status.status == WSS.WebLabSchedulingStatus.RESERVED_LOCAL:
            reservation = ConfirmedReservation(status.reservation_id, status.remaining_time, status.initial_configuration, status.url, "")
        elif status.status == WSS.WebLabSchedulingStatus.WAITING_INSTANCES:
            reservation = WaitingInstances(status.reservation_id, status.position)
        elif status.status == WSS.WebLabSchedulingStatus.POST_RESERVATION:
            reservation = PostReservationReservation(status.reservation_id, status.finished, status.initial_data, status.end_data)
        else:
            raise InvalidReservationStatusError( "Invalid reservation status.status: '%s'" % status.status)
        return reservation

    @staticmethod
    def translate_reservation_from_data(status_text, reservation_id, position, time, initial_configuration, end_data, url, finished, initial_data, remote_reservation_id):
        if status_text == Reservation.WAITING:
            reservation = WaitingReservation(reservation_id, position)
        elif status_text == Reservation.WAITING_CONFIRMATION:
            reservation = WaitingConfirmationReservation(reservation_id, url)
        elif status_text == Reservation.WAITING_INSTANCES:
            reservation = WaitingInstances(reservation_id, position)
        elif status_text == Reservation.CONFIRMED:
            reservation = ConfirmedReservation(reservation_id, time, initial_configuration, url, remote_reservation_id)
        elif status_text == Reservation.POST_RESERVATION:
            reservation = PostReservationReservation(reservation_id, finished, initial_data, end_data)
        else:
            raise InvalidReservationStatusError("Invalid reservation status_text: '%s'." % ( status_text ) )
        return reservation

    # XXX TODO: a new state would be required, but I don't have to deal with that
    def is_null(self):
        return isinstance(self, WaitingInstances) and self.position == NULL_POSITION

    @abstractmethod
    def to_status(self):
        """ Create a scheduling status """

class WaitingReservation(Reservation):
    def __init__(self, reservation_id, position):
        super(WaitingReservation,self).__init__(Reservation.WAITING, reservation_id)
        self.position = position

    def __repr__(self):
        return "WaitingReservation(reservation_id = %r, position = %r)" % (self.reservation_id.id, self.position)

    def to_status(self):
        return WSS.WaitingQueueStatus(self.reservation_id, self.position)

class ConfirmedReservation(Reservation):
    def __init__(self, reservation_id, time, initial_configuration, url, remote_reservation_id):
        super(ConfirmedReservation,self).__init__(Reservation.CONFIRMED, reservation_id)
        self.time                  = time
        self.initial_configuration = initial_configuration
        self.url                   = url
        self.remote_reservation_id = SessionId(remote_reservation_id)

    def __repr__(self):
        return "ConfirmedReservation(reservation_id = %r, time = %r, initial_configuration = %r, url = %r, remote_reservation_id = %r)" % (self.reservation_id.id, self.time, self.initial_configuration, self.url, self.remote_reservation_id.id)

    def to_status(self):
        return WSS.RemoteReservedStatus(self.reservation_id, self.time, self.initial_configuration, self.url, self.remote_reservation_id.id)

class WaitingConfirmationReservation(Reservation):
    def __init__(self, reservation_id, url):
        super(WaitingConfirmationReservation,self).__init__(Reservation.WAITING_CONFIRMATION, reservation_id)
        self.url = url

    def __repr__(self):
        return "WaitingConfirmationReservation(reservation_id = %r, url = %r)" % (self.reservation_id.id, self.url)

    def to_status(self):
        return WSS.WaitingConfirmationQueueStatus(self.reservation_id, self.url)

class WaitingInstances(Reservation):
    def __init__(self, reservation_id, position):
        super(WaitingInstances,self).__init__(Reservation.WAITING_INSTANCES, reservation_id)
        self.position = position

    def __repr__(self):
        return "WaitingInstances(reservation_id = %r, position = %r)" % (self.reservation_id.id, self.position)

    def to_status(self):
        return WSS.WaitingInstancesQueueStatus(self.reservation_id, self.position)

class NullReservation(WaitingInstances):
    def __init__(self):
        super(NullReservation, self).__init__('null reservation', NULL_POSITION)

class PostReservationReservation(Reservation):
    def __init__(self, reservation_id, finished, initial_data, end_data):
        super(PostReservationReservation,self).__init__(Reservation.POST_RESERVATION, reservation_id)
        self.finished     = finished
        self.initial_data = initial_data
        self.end_data     = end_data

    def __repr__(self):
        return "PostReservationReservation(reservation_id = %r, finished = %r, initial_data = %r, end_data = %r)" % (self.reservation_id.id, self.finished, self.initial_data, self.end_data)

    def to_status(self):
        return WSS.PostReservationStatus(self.reservation_id, self.finished, self.initial_data, self.end_data)

