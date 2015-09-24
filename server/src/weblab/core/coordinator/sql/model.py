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

import uuid
import datetime

from voodoo.dbutil import get_table_kwargs
from weblab.data.experiments import ExperimentId
from weblab.data.experiments import ExperimentInstanceId
import weblab.core.coordinator.exc as CoordExc

from weblab.core.coordinator.resource import Resource

from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, UniqueConstraint, Table, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
import sqlalchemy

Base = declarative_base()

class AlembicVersion(Base):
    """ Alembic is a database version manager for SQLAlchemy. This class
    represents the internal way of Alembic for managing versions.
    """
    __tablename__ = 'alembic_version'
    
    version_num = Column(String(32), nullable = False, primary_key = True)

    def __init__(self, version_num):
        self.version_num = version_num


def load():
    #
    # Place here all the dependences in order to populate Base
    #
    import weblab.core.coordinator.sql.priority_queue_scheduler_model as PriorityQueueSchedulerModel
    assert PriorityQueueSchedulerModel.Base == Base # Just to avoid pyflakes warnings

    import weblab.core.coordinator.sql.externals.weblabdeusto_scheduler_model as weblabdeusto_scheduler_model
    assert weblabdeusto_scheduler_model.Base == Base

    import weblab.core.coordinator.sql.externals.ilab_batch_scheduler_model as ilab_batch_scheduler_model
    assert ilab_batch_scheduler_model.Base == Base

TABLE_KWARGS = get_table_kwargs()

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
    name = Column(String(255), index = True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ResourceType(%r)" % self.name

class ResourceInstance(Base):
    __tablename__  = 'ResourceInstances'
    __table_args__ = (UniqueConstraint('resource_type_id', 'name'), TABLE_KWARGS)

    id = Column(Integer, primary_key = True)
    name = Column(String(255), index = True)

    resource_type_id = Column(Integer, ForeignKey("ResourceTypes.id"), index = True)
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

    resource_instance_id = Column(Integer, ForeignKey("ResourceInstances.id"), index = True)
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
        return "SchedulingSchemaIndependentSlotReservation(id=%r, current_resource_slot=%r)" % (id, self.current_resource_slot)

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
    exp_name = Column(String(255), index = True)
    cat_name = Column(String(255), index = True)

    resource_types = relation(ResourceType, secondary=t_experiment_type_has_or_had_resource_types, backref="experiment_types")

    def __init__(self, exp_name, cat_name):
        self.exp_name = exp_name
        self.cat_name = cat_name

    def to_experiment_id(self):
        return ExperimentId(self.exp_name, self.cat_name)

    def __repr__(self):
        return "ExperimentType(%r,%r)" % (self.exp_name, self.cat_name)

class ExperimentInstance(Base):
    __tablename__  = 'ExperimentInstances'
    __table_args__ = (UniqueConstraint('experiment_type_id','experiment_instance_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    laboratory_coord_address = Column(String(255))
    experiment_instance_id   = Column(String(255), index = True)

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
        return ExperimentInstanceId(self.experiment_instance_id, exp_id.exp_name, exp_id.cat_name)

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
    latest_access      = Column(DateTime, index = True)
    experiment_type_id = Column(Integer, ForeignKey('ExperimentTypes.id'))
    experiment_type    = relation(ExperimentType, backref=backref('reservations', order_by=id))
    # The initial data is provided by the client. It must be sent to the server as a first command.
    client_initial_data   = Column(Text)
    # The server initial data is provided by the server.
    server_initial_data   = Column(Text)
    # Request information, serialized in JSON: is the user using facebook? mobile? what's the user agent? what's the ip address?
    request_info          = Column(Text)

    _now = None

    def __init__(self, id, client_initial_data, server_initial_data, request_info, now):
        self.id = id
        if now is not None:
            Reservation._now = now
        else:
            Reservation._now = datetime.datetime.utcnow
        self.latest_access       = Reservation._now()
        self.client_initial_data = client_initial_data
        self.server_initial_data = server_initial_data
        self.request_info        = request_info

    def update(self):
        if Reservation._now is not None:
           self.latest_access = Reservation._now()

    @staticmethod
    def create(session_maker, experiment_id, client_initial_data, server_initial_data, request_info, now = None):
        MAX_TRIES = 10
        counter = 0
        while True:
            session = session_maker()
            try:
                id = str(uuid.uuid4())
                experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()
                if experiment_type is None:
                    raise CoordExc.ExperimentNotFoundError("Couldn't find experiment_type %s when creating Reservation" % experiment_id)

                reservation = Reservation(id, client_initial_data, server_initial_data, request_info, now)
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
        return "Reservation(%r, %r, %r, %r)" % (self.id, self.client_initial_data, self.server_initial_data, self.request_info)

###############################################################################
#
# One single reservation may fit in many independent schedulers. For instance,
# there could be a remote scheduler that wraps another WebLab-Deusto, and, at
# the same time, the same reservation is in a local queue. During a certain
# amount of time, where it is in different queues, it will be in both
# schedulers. However, as one of them finally decides that it is in
# WaitingConfirmation, Reserved or PostReservation status, the aggregator must
# know that the reservation should end in the rest of the schedulers.
# Subsequent calls to the aggregator should retrieve what active schedulers are
# there for that reservation id. In order to know which ones are active, this
# information is stored as records in this table.
#
class ActiveReservationSchedulerAssociation(Base):
    __tablename__  = 'ActiveReservationSchedulerAssociation'
    __table_args__ = TABLE_KWARGS

    id               = Column(Integer, primary_key = True)

    reservation_id   = Column(String(RESERVATION_ID_SIZE), nullable = False, index = True)

    #
    # Each Independent Aggregator is represented by an experiment type:
    # A "ud-dummy@Dummy experiments" might rely on different schedulers,
    # each identified by a resource type
    #
    experiment_type_id       = Column(Integer, ForeignKey('ExperimentTypes.id'), nullable = False)
    experiment_type          = relation(ExperimentType, backref=backref('reservation_scheduler_associations', order_by=id))

    #
    # Each Scheduler is represented by a resource_type
    #
    resource_type_id = Column(Integer, ForeignKey("ResourceTypes.id"), nullable = False)
    resource_type    = relation(ResourceType, backref=backref("reservation_scheduler_associations", order_by=id))

    def __init__(self, reservation_id, experiment_type, resource_type):
        self.reservation_id  = reservation_id
        self.experiment_type = experiment_type
        self.resource_type   = resource_type

    def __repr__(self):
        return "ActiveReservationSchedulerAssociation(reservation_id=%r, experiment_type=%r, resource_type=%r)" % (self.reservation_id, self.experiment_type, self.resource_type)

Index('ix_active_schedulers_reservation', ActiveReservationSchedulerAssociation.reservation_id, ActiveReservationSchedulerAssociation.experiment_type_id, ActiveReservationSchedulerAssociation.resource_type_id)
Index('ix_active_schedulers', ActiveReservationSchedulerAssociation.experiment_type_id, ActiveReservationSchedulerAssociation.resource_type_id)

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

    id                               = Column(String(RESERVATION_ID_SIZE), ForeignKey('Reservations.id'), primary_key = True, index = True)
    reservation                      = relation(Reservation, backref=backref('current_reservations', order_by=id))

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "CurrentReservation(id=%r, reservation=%r)" % (self.id, self.reservation)

######################################################################################
#
# Different threads and servers might try to finish a reservation for different
# reasons: user request to cancel a reservation, experiment notifying that the session
# should end, a timeout, etc. In order to coordinate them and avoid two concurrent
# calls to finish(), we use this temporal table. Every server trying to dispose a
# reservation will add the reservation_id. If they don't fail, they do the process.
# But if they fail because someone else added it first, they skip it.
#

class PendingToFinishReservation(Base):
    __tablename__  = 'PendingToFinishReservations'
    __table_args__ = TABLE_KWARGS

    id                               = Column(String(RESERVATION_ID_SIZE), primary_key = True)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "PendingToFinishReservation(id=%r)" % self.id

##########################################################################################
#
# Whenever a experiment finishes, it stores the information in the main database. However,
# it is still possible to retrieve this information from the scheduling database, in a
# status of PostReservationRetrievedData. For instance, if a user performs a reservation
# and the reservation is finished, it will enter in this status.
#

class PostReservationRetrievedData(Base):
    __tablename__  = 'PostReservationRetrievedData'
    __table_args__ = TABLE_KWARGS

    id                     = Column(Integer, primary_key=True)

    reservation_id         = Column(String(RESERVATION_ID_SIZE), index = True)
    finished               = Column(Boolean)                # Has the experiment finished?
    date                   = Column(DateTime)               # When did the experiment finish?
    expiration_date        = Column(DateTime, index = True) # When should this registry be removed?
    initial_data           = Column(Text)                   # A JSON structure with the information returned by the experiment server when initializing
                                                            # (useful for batch)
    end_data               = Column(Text)                   # A JSON structure with the information returned by the experiment server when disposing

    def __init__(self, reservation_id, finished, date, expiration_date, initial_data, end_data):
        self.reservation_id         = reservation_id
        self.date                   = date
        self.expiration_date        = expiration_date
        self.finished               = finished
        self.initial_data           = initial_data
        self.end_data               = end_data

    def __repr__(self):
        return "PostReservationRetrievedData(%r, %r, %r, %r, %r, %r, %r)" % (self.id, self.reservation_id, self.finished, self.date, self.expiration_date, self.initial_data, self.end_data)

