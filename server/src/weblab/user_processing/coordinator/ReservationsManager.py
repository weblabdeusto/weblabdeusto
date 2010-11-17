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

from weblab.user_processing.coordinator.CoordinatorModel import Reservation
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc

class ReservationsManager(object):
    def __init__(self, session_maker):
        self._session_maker = session_maker

    def _clean(self):
        session = self._session_maker()
        for reservation in session.query(Reservation).all():
            session.delete(reservation)
        session.commit()

    def create(self, now, latest_access = None):
        return Reservation.create(self._session_maker, now, latest_access)

    def check(self, session, reservation_id):
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        return reservation is not None

    def get_experiment_id(self, reservation_id):
        session = self._session_maker()
        try:
            reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
            if reservation is None:
                raise CoordExc.ExpiredSessionException("Expired reservation")
            return reservation.experiment_id
        finally:
            session.close()

    def update(self, session, reservation_id):
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation is None:
            session.close()
            raise CoordExc.ExpiredSessionException("Expired reservation")
        
        reservation.update()

    def list_expired_reservations(self, session, expiration_time):
        return ( expired_reservation.id for expired_reservation in session.query(Reservation).filter(Reservation.latest_access < expiration_time).all() )

    def delete(self, session, reservation_id):
        reservation = session.query(Reservation).filter_by(id=reservation_id).first()
        if reservation is not None:
            session.delete(reservation)

