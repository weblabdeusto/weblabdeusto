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

import time
import uuid
import json
import datetime

from weblab.data.experiments import ExperimentId
import weblab.core.coordinator.exc as CoordExc
from voodoo.typechecker import typecheck

from weblab.core.coordinator.redis.constants import (
    WEBLAB_RESERVATIONS,
    WEBLAB_RESERVATION,

    WEBLAB_RESOURCE_RESERVATIONS,
    WEBLAB_EXPERIMENT_TYPES,

    WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS,

    LATEST_ACCESS,
    CLIENT_INITIAL_DATA,
    SERVER_INITIAL_DATA,
    REQUEST_INFO,
    EXPERIMENT_TYPE,
)

class ReservationsManager(object):
    def __init__(self, redis_maker):
        self._redis_maker = redis_maker

    def _clean(self):
        client = self._redis_maker()

        for reservation_id in client.smembers(WEBLAB_RESERVATIONS):
            client.delete(WEBLAB_RESERVATION % reservation_id)
            client.delete(WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id)

        client.delete(WEBLAB_RESERVATIONS)

    def list_all_reservations(self):
        client = self._redis_maker()
        return client.smembers(WEBLAB_RESERVATIONS)

    @typecheck(ExperimentId, basestring, basestring, typecheck.ANY)
    def create(self, experiment_id, client_initial_data, request_info, now = None):
        client = self._redis_maker()
        serialized_client_initial_data = json.dumps(client_initial_data)
        server_initial_data = "{}"

        if now is None:
            now = datetime.datetime.utcnow
        
        current_moment = now()
        now_timestamp = time.mktime(current_moment.timetuple()) + current_moment.microsecond / 10e6

        MAX_TRIES = 10
        for _ in xrange(MAX_TRIES):
            reservation_id = str(uuid.uuid4())

            value = client.sadd(WEBLAB_RESERVATIONS, reservation_id)
            if value == 0:
                continue

            weblab_reservation = WEBLAB_RESERVATION % reservation_id
            client.hset(weblab_reservation, LATEST_ACCESS, now_timestamp)
            client.hset(weblab_reservation, REQUEST_INFO, request_info)
            client.hset(weblab_reservation, SERVER_INITIAL_DATA, server_initial_data)
            client.hset(weblab_reservation, CLIENT_INITIAL_DATA, serialized_client_initial_data)
            client.hset(weblab_reservation, EXPERIMENT_TYPE, experiment_id.to_weblab_str())

            weblab_resource_reservations = WEBLAB_RESOURCE_RESERVATIONS % experiment_id.to_weblab_str()
            client.sadd(weblab_resource_reservations, reservation_id)
            return reservation_id

        raise Exception("Couldn't create a session after %s tries" % MAX_TRIES)


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
        client = self._redis_maker()

        if not client.sismember(WEBLAB_EXPERIMENT_TYPES, experiment_id.to_weblab_str()):
            raise CoordExc.ExperimentNotFoundError("Experiment %s not found" % experiment_id)

        weblab_resource_reservations = WEBLAB_RESOURCE_RESERVATIONS % experiment_id.to_weblab_str()
        return list(client.smembers(weblab_resource_reservations))
        
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
