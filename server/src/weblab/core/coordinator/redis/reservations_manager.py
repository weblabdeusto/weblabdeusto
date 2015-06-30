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

import time
import uuid
import json
import datetime

from weblab.data.experiments import ExperimentId
import weblab.core.coordinator.exc as CoordExc
from voodoo.typechecker import typecheck
from voodoo.resources_manager import is_testing

from weblab.core.coordinator.redis.constants import (
    WEBLAB_RESERVATIONS_LOCK,
    WEBLAB_RESERVATIONS,
    WEBLAB_RESERVATION,
    WEBLAB_RESERVATION_STATUS,
    WEBLAB_RESERVATIONS_INDIVIDUAL_LOCK,

    WEBLAB_RESOURCE_RESERVATIONS,
    WEBLAB_EXPERIMENT_TYPES,

    WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS,
    WEBLAB_RESERVATIONS_FINISHING,

    CURRENT,
    LATEST_ACCESS,
    CLIENT_INITIAL_DATA,
    SERVER_INITIAL_DATA,
    REQUEST_INFO,
    EXPERIMENT_TYPE,
)

class ReservationsManager(object):
    def __init__(self, redis_maker):
        self._redis_maker = redis_maker
        self.now = datetime.datetime.utcnow

    def _clean(self):
        client = self._redis_maker()

        for reservation_id in client.smembers(WEBLAB_RESERVATIONS):
            client.delete(WEBLAB_RESERVATION % reservation_id)
            client.delete(WEBLAB_RESERVATION_STATUS % reservation_id)
            client.delete(WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id)
            client.delete(WEBLAB_RESERVATIONS_INDIVIDUAL_LOCK % reservation_id)

        client.delete(WEBLAB_RESERVATIONS_LOCK)
        client.delete(WEBLAB_RESERVATIONS)

    def list_all_reservations(self):
        client = self._redis_maker()
        return client.smembers(WEBLAB_RESERVATIONS)

    def lock_reservation(self, reservation_id, timeout = 10):
        client = self._redis_maker()
        individual_lock = WEBLAB_RESERVATIONS_INDIVIDUAL_LOCK % reservation_id
        initial = time.time()
        while not client.setnx(individual_lock, '') and time.time() < initial + 10:
            time.sleep(0.05)
        client.expire(individual_lock, 5)

    def unlock_reservation(self, reservation_id):
        client = self._redis_maker()
        client.delete(WEBLAB_RESERVATIONS_INDIVIDUAL_LOCK % reservation_id)

    @typecheck(ExperimentId, (basestring, dict), basestring, typecheck.ANY)
    def create(self, experiment_id, client_initial_data, request_info, now = None):
        client = self._redis_maker()
        serialized_client_initial_data = json.dumps(client_initial_data)
        server_initial_data = "{}"

        if now is None:
            now = datetime.datetime.utcnow
        else:
            self.now = now
        
        current_moment = now()
        now_timestamp = time.mktime(current_moment.timetuple()) + current_moment.microsecond / 1e6

        MAX_TRIES = 10
        for _ in xrange(MAX_TRIES):
            reservation_id = str(uuid.uuid4())

            value = client.sadd(WEBLAB_RESERVATIONS, reservation_id)
            if value == 0:
                continue

            weblab_reservation               = WEBLAB_RESERVATION % reservation_id
            weblab_reservation_status        = WEBLAB_RESERVATION_STATUS % reservation_id
            weblab_resource_reservations     = WEBLAB_RESOURCE_RESERVATIONS % experiment_id.to_weblab_str()

            reservation_data = {
                REQUEST_INFO        : request_info,
                SERVER_INITIAL_DATA : server_initial_data,
                CLIENT_INITIAL_DATA : serialized_client_initial_data,
                EXPERIMENT_TYPE     : experiment_id.to_weblab_str()
            }
            serialized_reservation_data = json.dumps(reservation_data)

            pipeline = client.pipeline()
            pipeline.hset(weblab_reservation_status, LATEST_ACCESS, now_timestamp)
            pipeline.set(weblab_reservation, serialized_reservation_data)
            pipeline.sadd(weblab_resource_reservations, reservation_id)
            pipeline.execute()

            return reservation_id

        raise Exception("Couldn't create a session after %s tries" % MAX_TRIES)

    def get_experiment_id(self, reservation_id):
        reservation_data = self.get_reservation_data(reservation_id)
        if reservation_data is None:
            raise CoordExc.ExpiredSessionError("Expired reservation: no experiment id found for that reservation (%s)" % reservation_id)
        return ExperimentId.parse(reservation_data[EXPERIMENT_TYPE])


    def get_reservation_data(self, reservation_id):
        client = self._redis_maker()
        weblab_reservation = WEBLAB_RESERVATION % reservation_id
        serialized_reservation_data = client.get(weblab_reservation)
        if serialized_reservation_data is None:
            return None
        else:
            return json.loads(serialized_reservation_data)

    def get_request_info_and_client_initial_data(self, reservation_id):
        reservation_data = self.get_reservation_data(reservation_id)
        if reservation_data is None:
            return "{}", "{}"
        return reservation_data[REQUEST_INFO], reservation_data[CLIENT_INITIAL_DATA]

    def update(self, reservation_id):
        client = self._redis_maker()
        
        current_moment = self.now()
        now_timestamp = time.mktime(current_moment.timetuple()) + current_moment.microsecond / 1e6

        weblab_reservation_status = WEBLAB_RESERVATION_STATUS % reservation_id
        
        expired = client.hset(weblab_reservation_status, LATEST_ACCESS, now_timestamp)
        # if it has created it, it means that it is expired
        return expired != 0


    def confirm(self, reservation_id):
        client = self._redis_maker()
        weblab_reservation        = WEBLAB_RESERVATION % reservation_id
        weblab_reservation_status = WEBLAB_RESERVATION_STATUS % reservation_id
        if not client.exists(weblab_reservation):
            raise CoordExc.ExpiredSessionError("Expired reservation")

        return client.hset(weblab_reservation_status, CURRENT, 1) != 0

    def downgrade_confirmation(self, reservation_id):
        client = self._redis_maker()
        weblab_reservation_status = WEBLAB_RESERVATION_STATUS % reservation_id
        return client.hdel(weblab_reservation_status, CURRENT) != 0

    def list_expired_reservations(self, expiration_time):
        expiration_timestamp = time.mktime(expiration_time.timetuple()) + expiration_time.microsecond / 1e6
        client = self._redis_maker()
        
        # This is not a problem in SQL, since we say "retrieve only those that have expired"
        # However, I simply don't know how to say that in redis, even using expire or expireat. 
        # The only way I can think of is to check the whole table of reservations. So we have
        # established a mechanism based on expiration to avoid performing this more than once per
        # second

        acquired = client.hset(WEBLAB_RESERVATIONS_LOCK, "locked", 1)
        if not acquired and not is_testing():
            # When testing, we want to avoid that two calls return different results, so 
            # we ignore the mechanism
            return []

        client.expire(WEBLAB_RESERVATIONS_LOCK, 1) # Every second

        reservation_ids = client.smembers(WEBLAB_RESERVATIONS)
        
        pipeline = client.pipeline()
        for reservation_id in reservation_ids:
            weblab_reservation_status = WEBLAB_RESERVATION_STATUS % reservation_id
            pipeline.hget(weblab_reservation_status, LATEST_ACCESS)

        expired_reservation_ids = []
        for reservation_id, latest_access_str in zip(reservation_ids, pipeline.execute()):
            if latest_access_str is None:
                continue
            latest_access = float(latest_access_str)
            if latest_access is not None and latest_access < expiration_timestamp:
                expired_reservation_ids.append(reservation_id)

        return expired_reservation_ids

    def list_sessions(self, experiment_id ):
        """ list_sessions( experiment_id ) -> [ session_id ] """
        client = self._redis_maker()

        if not client.sismember(WEBLAB_EXPERIMENT_TYPES, experiment_id.to_weblab_str()):
            raise CoordExc.ExperimentNotFoundError("Experiment %s not found" % experiment_id)

        weblab_resource_reservations = WEBLAB_RESOURCE_RESERVATIONS % experiment_id.to_weblab_str()
        return list(client.smembers(weblab_resource_reservations))
        
    def initialize_deletion(self, reservation_id):
        client = self._redis_maker()
        return client.sadd(WEBLAB_RESERVATIONS_FINISHING, reservation_id) != 0

    def clean_deletion(self, reservation_id):
        client = self._redis_maker()
        return client.srem(WEBLAB_RESERVATIONS_FINISHING, reservation_id)

    def delete(self, reservation_id):
        client = self._redis_maker()
      
        client.srem(WEBLAB_RESERVATIONS, reservation_id)
        weblab_reservation            = WEBLAB_RESERVATION                    % reservation_id
        weblab_reservation_status     = WEBLAB_RESERVATION_STATUS             % reservation_id
        weblab_reservation_schedulers = WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id
        client.delete(weblab_reservation, weblab_reservation_status, weblab_reservation_schedulers)

