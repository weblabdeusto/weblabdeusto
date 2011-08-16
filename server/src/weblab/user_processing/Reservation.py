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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import weblab.user_processing.coordinator.WebLabSchedulingStatus as WSS
import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions

class Reservation(object):
    WAITING              = "Reservation::waiting"
    WAITING_CONFIRMATION = "Reservation::waiting_confirmation"
    WAITING_INSTANCES    = "Reservation::waiting_instances"
    CONFIRMED            = "Reservation::confirmed"
    POST_RESERVATION     = "Reservation::post_reservation"
    def __init__(self, status):
        """ __init__(status)

        status is Reservation.WAITING, Reservation.CONFIRMED, etc.
        """
        super(Reservation,self).__init__()
        self.status = status

    def __repr__(self):
        return self.status

    @staticmethod
    def translate_reservation(status):
        if status.status == WSS.WebLabSchedulingStatus.WAITING:
            reservation = WaitingReservation(status.position)
        elif status.status == WSS.WebLabSchedulingStatus.WAITING_CONFIRMATION:
            reservation = WaitingConfirmationReservation()
        elif status.status == WSS.WebLabSchedulingStatus.RESERVED:
            reservation = ConfirmedReservation(
                    status.time,
                    status.initial_configuration
                )
        elif status.status == WSS.WebLabSchedulingStatus.WAITING_INSTANCES: #TODO: test me
            reservation = WaitingInstances(
                    status.position
                )
        elif status.status == WSS.WebLabSchedulingStatus.POST_RESERVATION: #TODO: test me
            reservation = PostReservationReservation(
                    status.end_data
                )
        else:
            raise UserProcessingExceptions.InvalidReservationStatusException(
                "Invalid reservation status.status: '%s'. Only '%s' and '%s' expected" % (
                    status.status, 
                    WSS.WebLabSchedulingStatus.WAITING, 
                    WSS.WebLabSchedulingStatus.RESERVED
                )
            )
        return reservation

    @staticmethod
    def translate_reservation_from_data(status_text, position = None, time = None, initial_configuration = None, end_data = None):
        if status_text == Reservation.WAITING:
            reservation = WaitingReservation(position)
        elif status_text == Reservation.WAITING_CONFIRMATION:
            reservation = WaitingConfirmationReservation()
        elif status_text == Reservation.WAITING_INSTANCES:
            reservation = WaitingInstances(position)
        elif status_text == Reservation.CONFIRMED:
            reservation = ConfirmedReservation(time, initial_configuration)
        elif status_text == Reservation.POST_RESERVATION:
            reservation = PostReservationReservation(end_data)
        else:
            raise UserProcessingExceptions.InvalidReservationStatusException("Invalid reservation status_text: '%s'." % ( status_text ) )
        return reservation

class WaitingReservation(Reservation):
    def __init__(self, position):
        super(WaitingReservation,self).__init__(Reservation.WAITING)
        self.position = position
    def __repr__(self):
        return "WaitingReservation(position = %r)" % self.position

class ConfirmedReservation(Reservation):
    def __init__(self, time, initial_configuration):
        super(ConfirmedReservation,self).__init__(Reservation.CONFIRMED)
        self.time = time
        self.initial_configuration = initial_configuration
    def __repr__(self):
        return "ConfirmedReservation(time = %r, initial_configuration = %r)" % (self.time, self.initial_configuration)

class WaitingConfirmationReservation(Reservation):
    def __init__(self):
        super(WaitingConfirmationReservation,self).__init__(Reservation.WAITING_CONFIRMATION)
    def __repr__(self):
        return "WaitingConfirmationReservation()"

class WaitingInstances(Reservation):
    def __init__(self, position):
        super(WaitingInstances,self).__init__(Reservation.WAITING_INSTANCES)
        self.position = position
    def __repr__(self):
        return "WaitingInstances(position = %r)" % self.position

class PostReservationReservation(Reservation):
    def __init__(self, finished, initial_data, end_data):
        super(PostReservationReservation,self).__init__(Reservation.POST_RESERVATION)
        self.finished     = finished
        self.initial_data = initial_data
        self.end_data     = end_data
    def __repr__(self):
        return "PostReservationReservation(finished = %r, initial_data = %r, end_data = %r)" % (self.finished, self.initial_data, self.end_data)

