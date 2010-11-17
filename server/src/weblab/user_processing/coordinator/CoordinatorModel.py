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

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

Base = declarative_base()

def load():
    # 
    # Place here all the dependences in order to populate Base
    # 
    import weblab.user_processing.coordinator.PriorityQueueSchedulerModel as PriorityQueueSchedulerModel
    assert PriorityQueueSchedulerModel.Base == Base # Just to avoid pyflakes warnings

TABLE_KWARGS = {'mysql_engine' : 'InnoDB'}

class Reservation(Base):

    __tablename__  = 'Reservations'
    __table_args__ = TABLE_KWARGS

    id = Column(String(36), primary_key=True)
    latest_access = Column(DateTime)
    experiment_id = Column(String(255 * 2 + 1)) # XXX 255 * 2 + 1 since right now we support 255 characters for exp_name + 255 for cat_name + @

    _now = None

    def __init__(self, id, now):
        self.id = id
        Reservation._now = now
        self.latest_access  = Reservation._now()

    def update(self):
        self.latest_access = Reservation._now()

    @staticmethod
    def create(session_maker, experiment_id, now):
        MAX_TRIES = 10
        counter = 0
        while True:
            session = session_maker()
            id = str(uuid.uuid4())
            reservation = Reservation(id, now)
            reservation.experiment_id = experiment_id
            session.add(reservation)
            try:
                session.commit()
                return reservation.id
            except sqlalchemy.exceptions.IntegrityError:
                counter += 1
                if counter == MAX_TRIES:
                    raise Exception("Couldn't create a session after %s tries" % MAX_TRIES)
            finally:
                session.close()


