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

import traceback
from sqlalchemy.exc import IntegrityError, ConcurrentModificationError
from weblab.user_processing.coordinator.CoordinatorModel import PostReservationRetrievedData
import weblab.user_processing.coordinator.WebLabSchedulingStatus as WSS

class PostReservationDataManager(object):
    def __init__(self, session_maker, time_provider):
        self._session_maker = session_maker
        self.time_provider = time_provider

    def create(self, reservation_id, date, expiration_date, initial_data):
        session = self._session_maker()
        try:
            registry = PostReservationRetrievedData(reservation_id = reservation_id, finished = False, date = date, expiration_date = expiration_date, initial_data = initial_data, end_data = None)
            session.add(registry)
            session.commit()
        finally:
            session.close()

    def finish(self, reservation_id, end_data):
        session = self._session_maker()
        try:
            found = False
            reservation = session.query(PostReservationRetrievedData).filter(PostReservationRetrievedData.reservation_id == reservation_id).first()
            reservation.finished = True
            reservation.end_data = end_data
            session.update(reservation)
            session.commit()
        finally:
            session.close()
       

    def find(self, reservation_id):
        session = self._session_maker()
        try:
            found = False
            reservation = session.query(PostReservationRetrievedData).filter(PostReservationRetrievedData.reservation_id == reservation_id).first()
            if reservation is None:
                return None

            return WSS.PostReservationStatus(reservation.finished, reservation.initial_data, reservation.end_data)
        finally:
            session.close()
       

    ##############################################################
    # 
    # Clean expired PostReservationRetrievedData
    # 
    def clean_expired(self):
        session = self._session_maker()
        try:
            found = False
            for expired_data in session.query(PostReservationRetrievedData).filter(PostReservationRetrievedData.expiration_date < self.time_provider.get_datetime()).all():
                session.delete(expired_data)
                found = True

            if found:
                try:
                    session.commit()
                except (ConcurrentModificationError, IntegrityError):
                    # Somebody else did it
                    traceback.print_exc()
        finally:
            session.close()

    def _clean(self):
        session = self._session_maker()
        try:
            for registry in session.query(PostReservationRetrievedData).all():
                session.delete(registry)
            session.commit()
        finally:
            session.close()

