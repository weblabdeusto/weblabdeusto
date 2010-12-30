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
import datetime

import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc

from weblab.user_processing.coordinator.Resource import Resource

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
import sqlalchemy

Base = declarative_base()

def load():
    # 
    # Place here all the dependences in order to populate Base
    # 
    import weblab.user_processing.coordinator.PriorityQueueSchedulerModel as PriorityQueueSchedulerModel
    assert PriorityQueueSchedulerModel.Base == Base # Just to avoid pyflakes warnings

    import weblab.user_processing.coordinator.NewPriorityQueueSchedulerModel as NewPriorityQueueSchedulerModel
    assert NewPriorityQueueSchedulerModel.Base == Base # Just to avoid pyflakes warnings

TABLE_KWARGS = {'mysql_engine' : 'InnoDB'}

######################################################################################
# 
# A resource represents the actual device used by every experiment instance. They are
# requirements of the experiment instance (every experiment instance must have one and 
# only one resource instance, although a resource can be used by more than one 
# experiment instance). 
#
# There are resource types (such as "ud-pld-device-board1"), and there can be multiple
# instances of the resource type (such as "pld1-basement-of-eng-building") for each
# resource type.
# 
# Finally, the scheduling schemas will be built for each resource type.
# 

class ResourceType(Base):
    __tablename__  = 'ResourceTypes'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id = Column(Integer, primary_key = True)
    name = Column(String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ResourceType(%s)" % repr(self.name)

class ResourceInstance(Base):
    __tablename__  = 'ResourceInstances'
    __table_args__ = (UniqueConstraint('resource_type_id', 'name'), TABLE_KWARGS)

    id = Column(Integer, primary_key = True)
    name = Column(String(255))

    resource_type_id = Column(Integer, ForeignKey("ResourceTypes.id"))
    resource_type    = relation(ResourceType, backref=backref("instances", order_by=id))

    def __init__(self, resource_type, name):
        self.resource_type = resource_type
        self.name          = name

    @property
    def slot(self):
        if len(self.slots) == 0:
            return None
        return self.slots[0]

    def to_resource(self):
        return Resource(self.resource_type.name, self.name)

    def __repr__(self):
        return "ResourceInstance(%s, %s)" % (self.resource_type, repr(self.name))

######################################################################################
# 
# The administrator will define that there is a certain instance of a resource 
# somewhere. However, this instance might be broken, or currently unavailable for 
# maintainance. In order to keep the integrity, we have this intermediate table that
# will have a row per each working instance. If the experiment is broken, the row 
# will not be present.
# 
class CurrentResourceSlot(Base):
    __tablename__  = 'CurrentResourceSlots'
    __table_args__ = (UniqueConstraint('resource_instance_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key = True)

    resource_instance_id = Column(Integer, ForeignKey("ResourceInstances.id"))
    resource_instance    = relation(ResourceInstance, backref=backref("slots", order_by=id))

    def __init__(self, resource_instance):
        self.resource_instance = resource_instance

    @property
    def slot_reservation(self):
        if len(self.slot_reservations) > 0:
            return self.slot_reservations[0]
        return None

    def __repr__(self):
        return "CurrentResourceSlot(%s)" % repr(self.resource_instance)

######################################################################################
# 
# Two scheduling schemas might try to reserve a slot concurrently. Since each one 
# would try it in its own tables, there wouldn't be any conflict. Therefore this table
# is created, so a row in this table is added when a reservation is held, and it's 
# removed when it is finished.
# 
class SchedulingSchemaIndependentSlotReservation(Base):
    __tablename__  = 'SchedulingSchemaIndependentSlotReservations'
    __table_args__ = (UniqueConstraint('current_resource_slot_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key = True)

    current_resource_slot_id = Column(Integer, ForeignKey("CurrentResourceSlots.id"))
    current_resource_slot    = relation(CurrentResourceSlot, backref=backref("slot_reservations", order_by=id))

    def __init__(self, current_resource_slot):
        self.current_resource_slot = current_resource_slot

    def __repr__(self):
        return "SchedulingSchemaIndependentSlotReservation(%s)" % self.current_resource_slot

######################################################################################
# 
# An experiment is the software system that behaves as the student expects. The 
# student will ask for a "ud-binary@Electronics experiments", and the system will
# provide an experiment instance whose resource is available, such as 
# "exp1:ud-binary@Electronics experiments", which use the same CPLD as 
# "exp1:ud-pld@PLD experiments", or it uses "exp2:ud-binary@Electronics experiments"
# which uses the same FPGA as "exp1:ud-fpga@FPGA experiments"
# 
# Given an experiment type, one can find all the resource types accessing all the 
# experiment instances of the experiment type, and for each experiment instance
# checking the resource type of the resource instance associated to the experiment
# instance. However, if there are reservations and the experiment instance is 
# suddenly removed due to maintainance or whatever, given a reservation_id the 
# system will not know how to achieve the resource type since that path has been
# broken. Due to this, this aparently redundant table is built when the experiment
# instances are added.
# 
t_experiment_type_has_or_had_resource_types = Table('ExperimentTypeHasOrHadResourceTypes', Base.metadata,
    Column('experiment_type_id', Integer, ForeignKey('ExperimentTypes.id'), primary_key=True),
    Column('resource_type_id',   Integer, ForeignKey('ResourceTypes.id'),   primary_key=True)
)

class ExperimentType(Base):
    __tablename__  = 'ExperimentTypes'
    __table_args__ = (UniqueConstraint('exp_name', 'cat_name'), TABLE_KWARGS)

    id       = Column(Integer, primary_key = True)
    exp_name = Column(String(255))
    cat_name = Column(String(255))

    resource_types = relation(ResourceType, secondary=t_experiment_type_has_or_had_resource_types, backref="experiment_types")

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

    resource_instance_id     = Column(Integer, ForeignKey('ResourceInstances.id'))
    resource_instance        = relation(ResourceInstance, backref=backref('experiment_instances', order_by=id))

    def __init__(self, experiment_type, laboratory_coord_address, experiment_instance_id):
        self.experiment_type          = experiment_type
        self.laboratory_coord_address = laboratory_coord_address
        self.experiment_instance_id   = experiment_instance_id

    def to_experiment_instance_id(self):
        exp_id = self.experiment_type.to_experiment_id()
        return ExperimentInstanceId.ExperimentInstanceId(self.experiment_instance_id, exp_id.exp_name, exp_id.cat_name)

######################################################################################
# 
# 
RESERVATION_ID_SIZE = 36 # len(str(uuid.uuid4()))

class Reservation(Base):

    __tablename__  = 'Reservations'
    __table_args__ = TABLE_KWARGS

    id = Column(String(RESERVATION_ID_SIZE), primary_key=True)
    latest_access      = Column(DateTime)
    experiment_type_id = Column(Integer, ForeignKey('ExperimentTypes.id'))
    experiment_type    = relation(ExperimentType, backref=backref('reservations', order_by=id))

    _now = None

    def __init__(self, id, now):
        self.id = id
        if now is not None:
            Reservation._now = now
        else:
            Reservation._now = datetime.datetime.utcnow
        self.latest_access  = Reservation._now()

    def update(self):
        self.latest_access = Reservation._now()

    @staticmethod
    def create(session_maker, experiment_id, now):
        MAX_TRIES = 10
        counter = 0
        while True:
            session = session_maker()
            try:
                id = str(uuid.uuid4())
                experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first() 
                if experiment_type is None:
                    raise CoordExc.ExperimentNotFoundException("Couldn't find experiment_type %s when creating Reservation" % experiment_id)

                reservation = Reservation(id, now)
                reservation.experiment_type = experiment_type
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

######################################################################################
# 
# Since a reservation can apply to different scheduling schemas of different resource
# types, the system could try to promote the reservation to a current reservation in
# more than one queue at the same time. Since this can't be accepted, every scheduling
# schema must create an instance of CurrentReservation, so a single reservation can't
# be promoted twice
# 

class CurrentReservation(Base):
    __tablename__  = 'CurrentReservations'
    __table_args__ = TABLE_KWARGS

    id = Column(String(RESERVATION_ID_SIZE), ForeignKey('Reservations.id'), primary_key = True)
    reservation = relation(Reservation, backref=backref('current_reservations', order_by=id))

    def __init__(self, id):
        self.id = id
    
    def __repr__(self):
        return "CurrentReservation(%s)" % repr(self.reservation)

