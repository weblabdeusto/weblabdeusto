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

from voodoo.dbutil import get_table_kwargs
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Text, Index
from sqlalchemy.orm import relation, backref

from weblab.core.coordinator.sql.model import Base, RESERVATION_ID_SIZE, ResourceType, Reservation, SchedulingSchemaIndependentSlotReservation
from weblab.core.coordinator.sql.model import CurrentReservation as GlobalCurrentReservation

TABLE_KWARGS = get_table_kwargs()

SUFFIX = 'PQ_' # Priority Queue

class ConcreteCurrentReservation(Base):
    __tablename__  = SUFFIX + 'ConcreteCurrentReservations'
    __table_args__ = (UniqueConstraint('slot_reservation_id'), UniqueConstraint('current_reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    slot_reservation_id              = Column(Integer, ForeignKey('SchedulingSchemaIndependentSlotReservations.id'))
    slot_reservation                 = relation(SchedulingSchemaIndependentSlotReservation, backref=backref('pq_current_reservations', order_by=id))

    current_reservation_id           = Column(String(RESERVATION_ID_SIZE), ForeignKey('CurrentReservations.id'), index = True)
    current_reservation              = relation(GlobalCurrentReservation, backref=backref('pq_current_reservations'))

    # For how many seconds the user has access
    time                             = Column(Integer)

    # When did it started
    start_time                       = Column(Integer)

    # Are you counting with the initialization time in "time"?
    initialization_in_accounting     = Column(Boolean)

    timestamp_before                 = Column(Integer)
    timestamp_after                  = Column(Integer)

    expired_timestamp                = Column(Integer, index = True)

    priority                         = Column(Integer)
    lab_session_id                   = Column(String(255))
    initial_configuration            = Column(Text)
    exp_info                         = Column(Text)

    def __init__(self, slot_reservation, current_reservation_id, time, start_time, priority, initialization_in_accounting):
        self.slot_reservation              = slot_reservation
        self.current_reservation_id        = current_reservation_id
        self.time                          = time
        self.start_time                    = start_time
        self.priority                      = priority
        self.initialization_in_accounting  = initialization_in_accounting
        self.lab_session_id                = None
        self.initial_configuration         = None
        self.timestamp_before              = None
        self.timestamp_after               = None
        self.exp_info                      = None

    def set_timestamp_before(self, timestamp_before):
        self.timestamp_before = timestamp_before
        if self.initialization_in_accounting:
            self.expired_timestamp = self.time + timestamp_before

    def set_timestamp_after(self, timestamp_after):
        self.timestamp_after = timestamp_after
        if not self.initialization_in_accounting:
            self.expired_timestamp = self.time + timestamp_after

    def __repr__(self):
        return SUFFIX + "ConcreteCurrentReservation(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
                            self.slot_reservation,
                            self.current_reservation_id,
                            self.time,
                            self.lab_session_id,
                            self.start_time,
                            self.priority,
                            self.initial_configuration,
                            self.timestamp_before,
                            self.timestamp_after,
                            self.initialization_in_accounting,
                            self.exp_info,
                        )

# TODO: instead of doing this, make a new column which is already the sum of both, and make an index on that column
Index('ix_pq_concrete_with_initial',    ConcreteCurrentReservation.initialization_in_accounting, ConcreteCurrentReservation.timestamp_before, ConcreteCurrentReservation.time)
Index('ix_pq_concrete_without_initial', ConcreteCurrentReservation.initialization_in_accounting, ConcreteCurrentReservation.timestamp_after, ConcreteCurrentReservation.time)

class WaitingReservation(Base):
    __tablename__  = SUFFIX + 'WaitingReservations'
    __table_args__ = (UniqueConstraint('reservation_id','resource_type_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    resource_type_id             = Column(Integer, ForeignKey('ResourceTypes.id'), index = True)
    reservation_id               = Column(String(RESERVATION_ID_SIZE), ForeignKey('Reservations.id'), index = True)
    reservation                  = relation(Reservation, backref=backref('pq_waiting_reservations', order_by=id))
    time                         = Column(Integer)
    priority                     = Column(Integer)
    initialization_in_accounting = Column(Boolean)

    resource_type       = relation(ResourceType, backref=backref('pq_waiting_reservations', order_by=id))

    def __init__(self, resource_type, reservation_id, time, priority, initialization_in_accounting):
        self.resource_type                = resource_type
        self.reservation_id               = reservation_id
        self.time                         = time
        self.priority                     = priority
        self.initialization_in_accounting = initialization_in_accounting

    def __repr__(self):
        return SUFFIX + "WaitingReservation(%r, %r, %r, %r, %r)" % (
                    self.resource_type,
                    self.reservation_id,
                    self.time,
                    self.priority,
                    self.initialization_in_accounting
                )

Index('ix_pq_waiting_rese_reso', WaitingReservation.reservation_id, WaitingReservation.resource_type_id)
