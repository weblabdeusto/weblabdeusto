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

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint 
from sqlalchemy.orm import relation, backref

from weblab.user_processing.coordinator.CoordinatorModel import Base, RESERVATION_ID_SIZE, ResourceType, Reservation, SchedulingSchemaIndependentSlotReservation
from weblab.user_processing.coordinator.CoordinatorModel import CurrentReservation as GlobalCurrentReservation

TABLE_KWARGS = {'mysql_engine' : 'InnoDB'}

SUFFIX = 'PQ_' # Priority Queue

class ConcreteCurrentReservation(Base):
    __tablename__  = SUFFIX + 'ConcreteCurrentReservations'
    __table_args__ = (UniqueConstraint('slot_reservation_id'), UniqueConstraint('current_reservation_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    slot_reservation_id              = Column(Integer, ForeignKey('SchedulingSchemaIndependentSlotReservations.id'))
    slot_reservation                 = relation(SchedulingSchemaIndependentSlotReservation, backref=backref('pq_current_reservations', order_by=id))

    current_reservation_id           = Column(String(RESERVATION_ID_SIZE), ForeignKey('CurrentReservations.id'))
    current_reservation              = relation(GlobalCurrentReservation, backref=backref('pq_current_reservations'))

    time                             = Column(Integer)
    start_time                       = Column(Integer)
    priority                         = Column(Integer)
    lab_session_id                   = Column(String(255))

    def __init__(self, slot_reservation, current_reservation_id, time, start_time, priority):
        self.slot_reservation              = slot_reservation
        self.current_reservation_id        = current_reservation_id
        self.time                          = time
        self.lab_session_id                = None
        self.start_time                    = start_time
        self.priority                      = priority

    def __repr__(self):
        return SUFFIX + "ConcreteCurrentReservation(%s, %s, %s, %s, %s, %s)" % (
                            repr(self.slot_reservation),
                            repr(self.current_reservation_id),
                            repr(self.time),
                            repr(self.lab_session_id),
                            repr(self.start_time),
                            repr(self.priority),
                        )

class WaitingReservation(Base):
    __tablename__  = SUFFIX + 'WaitingReservations'
    __table_args__ = (UniqueConstraint('reservation_id','resource_type_id'), TABLE_KWARGS)

    id = Column(Integer, primary_key=True)

    resource_type_id    = Column(Integer, ForeignKey('ResourceTypes.id'))
    reservation_id      = Column(String(RESERVATION_ID_SIZE), ForeignKey('Reservations.id'))
    reservation         = relation(Reservation, backref=backref('pq_waiting_reservations', order_by=id))
    time                = Column(Integer)
    priority            = Column(Integer)

    resource_type       = relation(ResourceType, backref=backref('pq_waiting_reservations', order_by=id))

    def __init__(self, resource_type, reservation_id, time, priority):
        self.resource_type   = resource_type
        self.reservation_id  = reservation_id
        self.time            = time
        self.priority        = priority

    def __repr__(self):
        return SUFFIX + "WaitingReservation(%s, %s, %s, %s)" % (
                    repr(self.resource_type),
                    repr(self.reservation_id),
                    repr(self.time),
                    repr(self.priority),
                )
