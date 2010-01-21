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

import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

TABLE_KWARGS = {'mysql_engine' : 'InnoDB'}

class ExperimentType(Base):
    __tablename__  = 'ExperimentTypes'
    __table_args__ = (UniqueConstraint('exp_name', 'cat_name'), TABLE_KWARGS)

    id       = Column(Integer, primary_key = True)
    exp_name = Column(String(255))
    cat_name = Column(String(255))

    def __init__(self, exp_name, cat_name):
        self.exp_name = exp_name
        self.cat_name = cat_name
    def to_experiment_id(self):
        return ExperimentId.ExperimentId(self.exp_name, self.cat_name)

class ExperimentInstance(Base):
    __tablename__  = 'ExperimentInstances'
    __table_args__ = (UniqueConstraint('experiment_type_id','experiment_instance_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    laboratory_coord_address = Column(String(255))
    experiment_instance_id   = Column(String(255))

    experiment_type_id       = Column(Integer, ForeignKey('ExperimentTypes.id'))
    experiment_type          = relation(ExperimentType, backref=backref('instances', order_by=id))

    def __init__(self, experiment_type, laboratory_coord_address, experiment_instance_id):
        self.experiment_type          = experiment_type
        self.laboratory_coord_address = laboratory_coord_address
        self.experiment_instance_id   = experiment_instance_id

    def to_experiment_instance_id(self):
        exp_id = self.experiment_type.to_experiment_id()
        return ExperimentInstanceId.ExperimentInstanceId(self.experiment_instance_id, exp_id.exp_name, exp_id.cat_name)

    @property
    def current_reservation(self):
        if len(self.current_reservations) == 0:
            return None
        else:
            return self.current_reservations[0]

class Reservation(Base):

    __tablename__  = 'Reservations'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)
    latest_access = Column(DateTime)

    _now = None

    def __init__(self, now, latest_access = None):
        Reservation._now = now
        if latest_access is None:
            self.latest_access  = Reservation._now()
        else:
            self.latest_access  = latest_access

    def update(self):
        self.latest_access = Reservation._now()

    @property
    def current_reservation(self):
        current_reservations = self.current_reservations
        if len(current_reservations) == 0:
            return None
        else:
            return current_reservations[0]

    @property
    def waiting_reservation(self):
        waiting_reservations = self.waiting_reservations
        if len(waiting_reservations) == 0:
            return None
        else:
            return waiting_reservations[0]

class CurrentReservation(Base):
    __tablename__  = 'CurrentReservations'
    __table_args__ = (UniqueConstraint('experiment_instance_id'), UniqueConstraint('reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    experiment_instance_id = Column(Integer, ForeignKey('ExperimentInstances.id'))
    reservation_id         = Column(Integer, ForeignKey('Reservations.id'))
    time                   = Column(Integer)
    start_time             = Column(Integer)
    priority               = Column(Integer)
    lab_session_id         = Column(String(255))

    experiment_instance    = relation(ExperimentInstance, backref=backref('current_reservations', order_by=id))
    reservation            = relation(Reservation, backref=backref('current_reservations', order_by=id))

    def __init__(self, experiment_instance, reservation, time, start_time, priority):
        self.experiment_instance = experiment_instance
        self.reservation         = reservation
        self.time                = time
        self.lab_session_id      = None
        self.start_time          = start_time
        self.priority            = priority

class WaitingReservation(Base):
    __tablename__  = 'WaitingReservations'
    __table_args__ = (UniqueConstraint('reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    experiment_type_id = Column(Integer, ForeignKey('ExperimentTypes.id'))
    reservation_id     = Column(Integer, ForeignKey('Reservations.id'))
    time               = Column(Integer)
    priority           = Column(Integer)

    experiment_type    = relation(ExperimentType, backref=backref('waiting_reservations', order_by=id))
    reservation        = relation(Reservation, backref=backref('waiting_reservations', order_by=id))

    def __init__(self, experiment_type, reservation, time, priority):
        self.experiment_type = experiment_type
        self.reservation     = reservation
        self.time            = time
        self.priority        = priority

