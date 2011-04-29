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

from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, UniqueConstraint, Table, Text
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
        return "ResourceType(%r)" % self.name

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
        return "ResourceInstance(%r, %r)" % (self.resource_type, self.name)

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
        return "CurrentResourceSlot(%r)" % self.resource_instance

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
        return "SchedulingSchemaIndependentSlotReservation(%r)" % self.current_resource_slot

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

    def __repr__(self):
        return "ExperimentType(%r,%r)" % (self.exp_name, self.cat_name)


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

    def __repr__(self):
        return "ExperimentInstance(%r,%r,%r)" % (self.experiment_type, self.laboratory_coord_address, self.experiment_instance_id)

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
    # The initial data is provided by the client. It must be sent to the server as a first command.
    client_initial_data   = Column(Text)
    # The server initial data is provided by the server.
    server_initial_data   = Column(Text)

    _now = None

    def __init__(self, id, client_initial_data, server_initial_data, now):
        self.id = id
        if now is not None:
            Reservation._now = now
        else:
            Reservation._now = datetime.datetime.utcnow
        self.latest_access       = Reservation._now()
        self.client_initial_data = client_initial_data
        self.server_initial_data = server_initial_data

    def update(self):
        if Reservation._now is not None:
           self.latest_access = Reservation._now()

    @staticmethod
    def create(session_maker, experiment_id, client_initial_data, server_initial_data, now = None):
        MAX_TRIES = 10
        counter = 0
        while True:
            session = session_maker()
            try:
                id = str(uuid.uuid4())
                experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first() 
                if experiment_type is None:
                    raise CoordExc.ExperimentNotFoundException("Couldn't find experiment_type %s when creating Reservation" % experiment_id)

                reservation = Reservation(id, client_initial_data, server_initial_data, now)
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

    def __repr__(self):
        return "Reservation(%r, %r, %r)" % (self.id, self.client_initial_data, self.server_initial_data)

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

    id                               = Column(String(RESERVATION_ID_SIZE), ForeignKey('Reservations.id'), primary_key = True)
    reservation                      = relation(Reservation, backref=backref('current_reservations', order_by=id))

    # 
    # While initializing, the system will have to keep asking the experiment server if it has
    # been initialized every few time. This time is defined by the experiment server. For 
    # instance, it could say "don't ask me in 30 seconds", or "please ask me in 0.2 seconds".
    # However, given that there are different servers asking for the state concurrently, the
    # table must check that only one of them calls the is_initializing method.
    # 
    # While this could be implemented as a set of commands, the purpose of the is_initializing
    # method is to avoid being taken into account in the time restrictions of the experiment.
    # For instance, in the University of Deusto we have experiments which use Xilinx devices,
    # and the devices can be programmed with a serial port or with a JTAG Blazer, and they
    # will take more or less time. If you establish that a user has 3 minutes, and depending on
    # the device being used it will become 2 minutes, problems arise.
    # 
    # If all the fields below are set to NULL, it means that it has finish the initialization
    #
    # Therefore, once a server performs a call, it will store the result, establishing:
    # 
    # - When the latest initialization finished
    # 

    latest_initialization            = Column(DateTime)

    # 
    # - How long in milliseconds the servers should wait
    # 
    next_initialization_milliseconds = Column(Integer)

    #
    # - If an initialization process is being held at the moment. This is a call to the 
    #   is_initializing() method, not the fact of being initialized.
    #
    currently_calling_initialization = Column(Boolean)

    # 
    # - Who is initializing the system. If two processes see that currently_calling_initialization 
    #   is false and that it's time to query is_initializing, and both set currently_calling_initialization 
    #   true,  both could query. In order to avoid this, they also have to sign that they're the 
    #   one who will actually perform the task and later check that they're the one who do this.
    # 
    initializer                      = Column(String(30)) # Something like "Thread-10@process1"

    # 
    # The same concepts can be applied to the resource disposal
    # 

    latest_disposal                  = Column(DateTime)

    next_disposal_milliseconds       = Column(Integer)

    currently_calling_disposal       = Column(Boolean)

    disposer                         = Column(String(30))

    def __init__(self, id, latest_initialization = None, next_initialization_milliseconds = None, latest_disposal = None, next_disposal_milliseconds = None):
        self.id = id

        self.latest_initialization            = latest_initialization
        self.next_initialization_milliseconds = next_initialization_milliseconds
        self.currently_calling_initialization = False
        self.initializer                      = None

        self.latest_disposal                  = latest_disposal
        self.next_disposal_milliseconds       = next_disposal_milliseconds
        self.currently_calling_disposal       = False
        self.disposer                         = None


    def next_initialization(self, now, millis):
        self.latest_initialization            = now
        self.next_initialization_milliseconds = millis

    def is_initialized(self):
        return self.latest_initialization is None or self.next_initialization_milliseconds is None

    def next_disposal(self, now, millis):
        self.latest_disposal            = now
        self.next_disposal_milliseconds = millis

    def is_disposed(self):
        return self.latest_disposal is None or self.next_disposal_milliseconds is None

    def __repr__(self):
        return "CurrentReservation(%r, %r, %r, %r, %r, %r, %r, %r, %r)" % (self.reservation, self.latest_initialization, self.next_initialization_milliseconds, self.currently_calling_initialization, self.initializer, self.latest_disposal, self.next_disposal_milliseconds, self.currently_calling_disposal, self.disposer)

######################################################################################
# 
# Batch experiments are executed and once they finish, the information they returned
# is stored in this table. Later the core server will check for this information and
# it will periodically delete expired information, as well as it will gather 
# information that the user asks for and will store it in the proper user tables at
# core level.
# 

class BatchRetrievedData(Base):
    __tablename__  = 'BatchRetrievedData'
    __table_args__ = TABLE_KWARGS

    id                     = Column(Integer, primary_key=True)

    reservation_id         = Column(String(RESERVATION_ID_SIZE))
    date                   = Column(DateTime)    # When did the experiment finish?
    experiment_instance_id = Column(String(512)) # exp1:ud-pld@PLD experiments
    returned_data          = Column(Text)        # A JSON structure with the information returned by the experiment server

    def __init__(self, reservation_id, date, experiment_instance_id, returned_data):
        self.reservation_id         = reservation_id
        self.date                   = date
        self.experiment_instance_id = experiment_instance_id
        self.returned_data          = returned_data
    
    def __repr__(self):
        return "BatchRetrievedData(%r, %r, %r, %r, %r)" % (self.id, self.reservation_id, self.date, self.experiment_instance_id, self.returned_data)

