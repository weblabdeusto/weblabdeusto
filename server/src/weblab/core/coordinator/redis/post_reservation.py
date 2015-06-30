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

import datetime
import json

from voodoo.typechecker import typecheck

import weblab.core.coordinator.status as WSS

from weblab.core.coordinator.redis.constants import (
    WEBLAB_POST_RESERVATION,
    WEBLAB_POST_RESERVATIONS,

    FINISHED,
    INITIAL_DATA,
    END_DATA,
)

class PostReservationDataManager(object):
    def __init__(self, redis_maker, time_provider):
        self._redis_maker   = redis_maker
        self.time_provider  = time_provider
        self.force_deletion = False

    @typecheck(basestring, datetime.datetime, datetime.datetime, basestring)
    def create(self, reservation_id, date, expiration_date, initial_data):
        client = self._redis_maker()
        
        pipeline = client.pipeline()
    
        weblab_post_reservation = WEBLAB_POST_RESERVATION % reservation_id
        obj = json.dumps({ INITIAL_DATA : initial_data, FINISHED : False })

        pipeline.sadd(WEBLAB_POST_RESERVATIONS, reservation_id)
        pipeline.set(weblab_post_reservation, obj)
        time_difference = expiration_date - datetime.datetime.utcnow()
        remaining_seconds = time_difference.days * 3600 * 24 + time_difference.seconds
        pipeline.expire(weblab_post_reservation, remaining_seconds)

        pipeline.execute()

    @typecheck(basestring)
    def delete(self, reservation_id):
        client = self._redis_maker()
        pipeline = client.pipeline()
        pipeline.srem(WEBLAB_POST_RESERVATIONS, reservation_id)
        pipeline.delete(WEBLAB_POST_RESERVATION % reservation_id)
        pipeline.execute()
    
    @typecheck(basestring, basestring)
    def finish(self, reservation_id, end_data):
        client = self._redis_maker()

        weblab_post_reservation = WEBLAB_POST_RESERVATION % reservation_id

        post_reservation_data_str = client.get(weblab_post_reservation)
        if post_reservation_data_str is None:
            return

        post_reservation_data = json.loads(post_reservation_data_str)
        post_reservation_data[END_DATA] = end_data
        post_reservation_data[FINISHED] = True
        post_reservation_data_str = json.dumps(post_reservation_data)
        client.set(weblab_post_reservation, post_reservation_data_str)

    @typecheck(basestring)
    def find(self, reservation_id):
        client = self._redis_maker()

        weblab_post_reservation = WEBLAB_POST_RESERVATION % reservation_id

        post_reservation_data_str = client.get(weblab_post_reservation)
        if post_reservation_data_str is None:
            return None
        
        post_reservation_data = json.loads(post_reservation_data_str)
        return WSS.PostReservationStatus(reservation_id, post_reservation_data[FINISHED], post_reservation_data[INITIAL_DATA], post_reservation_data.get(END_DATA))


    ##############################################################
    #
    # Clean expired PostReservationRetrievedData
    #
    def clean_expired(self):
        # Redis expires objects automatically. Here we just remove those dead references
        # However, we let the tester to force deletion

        if self.force_deletion:
            self._clean()

        client = self._redis_maker()
        post_reservations = client.smembers(WEBLAB_POST_RESERVATIONS)

        if len(post_reservations) == 0:
            return

        pipeline = client.pipeline()
        for reservation_id in post_reservations:
            pipeline.get(WEBLAB_POST_RESERVATION % reservation_id)
        
        dead_reservation_ids = []
        for reservation_id, result in zip(post_reservations, pipeline.execute()):
            if result is None:
                dead_reservation_ids.append(WEBLAB_POST_RESERVATION % reservation_id)
        
        if len(dead_reservation_ids) > 0:
            client.delete(*dead_reservation_ids)

    def _clean(self):
        client = self._redis_maker()

        for reservation_id in client.smembers(WEBLAB_POST_RESERVATIONS):
            client.delete(WEBLAB_POST_RESERVATION % reservation_id)

        client.delete(WEBLAB_POST_RESERVATIONS)

