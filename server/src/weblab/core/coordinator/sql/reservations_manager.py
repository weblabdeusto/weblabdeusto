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

from weblab.core.coordinator.sql.model import Reservation, CurrentReservation, ExperimentType, PendingToFinishReservation
import weblab.core.coordinator.exc as CoordExc

from sqlalchemy.exc import IntegrityError, OperationalError 
from sqlalchemy.orm.exc import ConcurrentModificationError

import json

class ReservationsManager(object):
    def __init__(self, session_maker):
        self._session_maker = session_maker

    def _clean(self):
        session = self._session_maker()
        try:
            for current_reservation in session.query(CurrentReservation).all():
                session.delete(current_reservation)
            for reservation in session.query(Reservation).all():
                session.delete(reservation)
            session.commit()
        finally:
            session.close()

    def create(self, experiment_type, client_initial_data, request_info, now = None):
        serialized_client_initial_data = json.dumps(client_initial_data)
        server_initial_data = "{}"
        return Reservation.create(self._session_maker, experiment_type, serialized_client_initial_data, server_initial_data, request_info, now)

    def check(self, session, reservation_id):
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        return reservation is not None

    def get_experiment_id(self, reservation_id):
        session = self._session_maker()
        try:
            reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
            if reservation is None:
                raise CoordExc.ExpiredSessionError("Expired reservation: no experiment id found for that reservation (%s)" % reservation_id)
            return reservation.experiment_type.to_experiment_id()
        finally:
            session.close()

    def get_request_info_and_client_initial_data(self, reservation_id):
        session = self._session_maker()
        try:
            reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
            if reservation is None:
                return "{}", "{}"
            return reservation.request_info, reservation.client_initial_data
        finally:
            session.close()

    def update(self, session, reservation_id):
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation is None:
            raise CoordExc.ExpiredSessionError("Expired reservation")

        reservation.update()

    def confirm(self, session, reservation_id):
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation is None:
            raise CoordExc.ExpiredSessionError("Expired reservation")

        current_reservation = CurrentReservation(reservation.id)
        session.add(current_reservation)

    def downgrade_confirmation(self, session, reservation_id):
        current_reservation = session.query(CurrentReservation).filter(CurrentReservation.id == reservation_id).first()
        if current_reservation is None:
            return # Already downgraded
        session.delete(current_reservation)

    def list_expired_reservations(self, session, expiration_time):
        return ( expired_reservation.id for expired_reservation in session.query(Reservation).filter(Reservation.latest_access < expiration_time).all() )

    def list_sessions(self, experiment_id ):
        """ list_sessions( experiment_id ) -> [ session_id ] """
        session = self._session_maker()
        try:
            experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()
            if experiment_type is None:
                raise CoordExc.ExperimentNotFoundError("Experiment %s not found" % experiment_id)

            reservation_ids = []

            for reservation in experiment_type.reservations:
                reservation_ids.append(reservation.id)

        finally:
            session.close()

        return reservation_ids

    def initialize_deletion(self, reservation_id):
        session = self._session_maker()
        try:
            pending = PendingToFinishReservation(reservation_id)
            session.add(pending)
            try:
                session.commit()
                return True
            except (IntegrityError, OperationalError, ConcurrentModificationError):
                # Somebody else is deleting it
                return False
        finally:
            session.close()

    def clean_deletion(self, reservation_id):
        session = self._session_maker()
        try:
            pending_to_finish = session.query(PendingToFinishReservation).filter_by(id=reservation_id).first()
            if pending_to_finish is not None:
                session.delete(pending_to_finish)
            session.commit()
        finally:
            session.close()

    def delete(self, session, reservation_id):
        reservation = session.query(Reservation).filter_by(id=reservation_id).first()
        if reservation is not None:
            current_reservation = session.query(CurrentReservation).filter_by(id=reservation_id).first()
            if current_reservation is not None:
                session.delete(current_reservation)
            session.delete(reservation)
