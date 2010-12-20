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

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Binary
from sqlalchemy.orm import relation, backref

from weblab.user_processing.coordinator.CoordinatorModel import Base

TABLE_KWARGS = {'mysql_engine' : 'InnoDB'}

SUFFIX = 'PQ_' # Priority Queue

class ExperimentType(Base):
    __tablename__  = SUFFIX + 'ExperimentTypes'
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
    __tablename__  = SUFFIX + 'ExperimentInstances'
    __table_args__ = (UniqueConstraint('experiment_type_id','experiment_instance_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    laboratory_coord_address = Column(String(255))
    experiment_instance_id   = Column(String(255))

    experiment_type_id       = Column(Integer, ForeignKey(SUFFIX + 'ExperimentTypes.id'))
    experiment_type          = relation(ExperimentType, backref=backref('instances', order_by=id))

    def __init__(self, experiment_type, laboratory_coord_address, experiment_instance_id):
        self.experiment_type          = experiment_type
        self.laboratory_coord_address = laboratory_coord_address
        self.experiment_instance_id   = experiment_instance_id

    def to_experiment_instance_id(self):
        exp_id = self.experiment_type.to_experiment_id()
        return ExperimentInstanceId.ExperimentInstanceId(self.experiment_instance_id, exp_id.exp_name, exp_id.cat_name)

    @property
    def available(self):
        if len(self.availables) == 0:
            return None
        else:
            return self.availables[0]

##############################################################################
# 
# If it's broken, then there is no instance of AvailableExperimentInstance
# 
class AvailableExperimentInstance(Base):
    __tablename__   = SUFFIX + 'AvailableExperimentInstances'
    __table_args__  = (UniqueConstraint('experiment_instance_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    experiment_instance_id = Column(Integer, ForeignKey(SUFFIX +'ExperimentInstances.id'))

    experiment_instance    = relation(ExperimentInstance, backref=backref('availables', order_by=id))

    def __init__(self, experiment_instance):
        self.experiment_instance = experiment_instance

    @property
    def current_reservation(self):
        if len(self.current_reservations) == 0:
            return None
        else:
            return self.current_reservations[0]


class CurrentReservation(Base):
    __tablename__  = SUFFIX + 'CurrentReservations'
    __table_args__ = (UniqueConstraint('available_experiment_instance_id'), UniqueConstraint('reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    available_experiment_instance_id = Column(Integer, ForeignKey(SUFFIX + 'AvailableExperimentInstances.id'))
    reservation_id                   = Column(String(36))
    time                             = Column(Integer)
    start_time                       = Column(Integer)
    priority                         = Column(Integer)
    lab_session_id                   = Column(String(255))
    # The initial data is provided by the client. It must be sent to the server as a first command.
    client_initial_data              = Column(Binary)
    # The initial configuration is provided by the server.
    initial_configuration            = Column(Binary)

    available_experiment_instance    = relation(AvailableExperimentInstance, backref=backref('current_reservations', order_by=id))

    def __init__(self, available_experiment_instance, reservation_id, time, start_time, priority, client_initial_data):
        self.available_experiment_instance = available_experiment_instance
        self.reservation_id                = reservation_id
        self.time                          = time
        self.lab_session_id                = None
        self.start_time                    = start_time
        self.priority                      = priority
        self.initial_configuration         = None

class WaitingReservation(Base):
    __tablename__  = SUFFIX + 'WaitingReservations'
    __table_args__ = (UniqueConstraint('reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    experiment_type_id  = Column(Integer, ForeignKey(SUFFIX + 'ExperimentTypes.id'))
    reservation_id      = Column(String(36))
    time                = Column(Integer)
    priority            = Column(Integer)
    client_initial_data = Column(Binary)

    experiment_type     = relation(ExperimentType, backref=backref('waiting_reservations', order_by=id))

    def __init__(self, experiment_type, reservation_id, time, priority, client_initial_data):
        self.experiment_type = experiment_type
        self.reservation_id  = reservation_id
        self.time            = time
        self.priority        = priority
        self.client_initial_data    = client_initial_data

