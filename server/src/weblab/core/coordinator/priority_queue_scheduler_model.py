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

from voodoo.dbutil import get_table_kwargs
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relation, backref

from weblab.core.coordinator.model import Base, RESERVATION_ID_SIZE, ResourceType, Reservation, SchedulingSchemaIndependentSlotReservation
from weblab.core.coordinator.model import CurrentReservation as GlobalCurrentReservation

TABLE_KWARGS = get_table_kwargs()

SUFFIX = 'PQ_' # Priority Queue

class ConcreteCurrentReservation(Base):
    __tablename__  = SUFFIX + 'ConcreteCurrentReservations'
    __table_args__ = (UniqueConstraint('slot_reservation_id'), UniqueConstraint('current_reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    slot_reservation_id              = Column(Integer, ForeignKey('SchedulingSchemaIndependentSlotReservations.id'))
    slot_reservation                 = relation(SchedulingSchemaIndependentSlotReservation, backref=backref('pq_current_reservations', order_by=id))

    current_reservation_id           = Column(String(RESERVATION_ID_SIZE), ForeignKey('CurrentReservations.id'))
    current_reservation              = relation(GlobalCurrentReservation, backref=backref('pq_current_reservations'))

    # For how many seconds the user has access
    time                             = Column(Integer)

    # When did it started
    start_time                       = Column(Integer)

    # Are you counting with the initialization time in "time"?
    initialization_in_accounting     = Column(Boolean)

    timestamp_before                 = Column(Integer)
    timestamp_after                  = Column(Integer)

    priority                         = Column(Integer)
    lab_session_id                   = Column(String(255))
    initial_configuration            = Column(Text)

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

    def __repr__(self):
        return SUFFIX + "ConcreteCurrentReservation(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
                            self.slot_reservation,
                            self.current_reservation_id,
                            self.time,
                            self.lab_session_id,
                            self.start_time,
                            self.priority,
                            self.initial_configuration,
                            self.timestamp_before,
                            self.timestamp_after,
                            self.initialization_in_accounting
                        )

class WaitingReservation(Base):
    __tablename__  = SUFFIX + 'WaitingReservations'
    __table_args__ = (UniqueConstraint('reservation_id','resource_type_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    resource_type_id             = Column(Integer, ForeignKey('ResourceTypes.id'))
    reservation_id               = Column(String(RESERVATION_ID_SIZE), ForeignKey('Reservations.id'))
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

