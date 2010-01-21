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

import weblab.user_processing.coordinator.WebLabQueueStatus as WebLabQueueStatus
import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions

class Reservation(object):
    WAITING              = "Reservation::waiting"
    WAITING_CONFIRMATION = "Reservation::waiting_confirmation"
    WAITING_INSTANCES    = "Reservation::waiting_instances"
    CONFIRMED            = "Reservation::confirmed"
    CANCELLING           = "Reservation::cancelling"
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
        if status.status == WebLabQueueStatus.WebLabQueueStatus.WAITING:
            reservation = WaitingReservation(status.position)
        elif status.status == WebLabQueueStatus.WebLabQueueStatus.WAITING_CONFIRMATION:
            reservation = WaitingConfirmationReservation()
        elif status.status == WebLabQueueStatus.WebLabQueueStatus.RESERVED:
            reservation = ConfirmedReservation(
                    status.time
                )
        elif status.status == WebLabQueueStatus.WebLabQueueStatus.WAITING_INSTANCES: #TODO: test me
            reservation = WaitingInstances(
                    status.position
                )
        elif status.status == WebLabQueueStatus.WebLabQueueStatus.CANCELLING: #TODO: test me
            reservation = CancellingReservation()
        else:
            raise UserProcessingExceptions.InvalidReservationStatusException(
                "Invalid reservation status.status: '%s'. Only '%s' and '%s' expected" % (
                    status.status, 
                    WebLabQueueStatus.WebLabQueueStatus.WAITING, 
                    WebLabQueueStatus.WebLabQueueStatus.RESERVED
                )
            )
        return reservation

    @staticmethod
    def translate_reservation_from_data(status_text, position=None, time=None):
        if status_text == Reservation.WAITING:
            reservation = WaitingReservation(position)
        elif status_text == Reservation.WAITING_CONFIRMATION:
            reservation = WaitingConfirmationReservation()
        elif status_text == Reservation.WAITING_INSTANCES:
            reservation = WaitingInstances(position)
        elif status_text == Reservation.CONFIRMED:
            reservation = ConfirmedReservation(time)
        elif status_text == Reservation.CANCELLING:
            reservation = CancellingReservation()
        else:
            raise UserProcessingExceptions.InvalidReservationStatusException("Invalid reservation status_text: '%s'." % ( status_text ) )
        return reservation

class WaitingReservation(Reservation):
    def __init__(self, position):
        super(WaitingReservation,self).__init__(Reservation.WAITING)
        self.position = position
    def __repr__(self):
        return "<WaitingReservation position = %i>" % self.position

class ConfirmedReservation(Reservation):
    def __init__(self, time):
        super(ConfirmedReservation,self).__init__(Reservation.CONFIRMED)
        self.time = time
    def __repr__(self):
        return "<ConfirmedReservation time = %s>" % self.time

class WaitingConfirmationReservation(Reservation):
    def __init__(self):
        super(WaitingConfirmationReservation,self).__init__(Reservation.WAITING_CONFIRMATION)
    def __repr__(self):
        return "<WaitingConfirmationReservation>"

class WaitingInstances(Reservation):
    def __init__(self, position):
        super(WaitingInstances,self).__init__(Reservation.WAITING_INSTANCES)
        self.position = position
    def __repr__(self):
        return "<WaitingInstances position = %i>" % self.position

class CancellingReservation(Reservation):
    def __init__(self):
        super(CancellingReservation,self).__init__(Reservation.CANCELLING)
    def __repr__(self):
        return "<CancellingReservation>"

