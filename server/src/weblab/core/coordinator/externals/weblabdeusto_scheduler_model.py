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

from voodoo.typechecker import typecheck
from voodoo.dbutil import get_table_kwargs
from sqlalchemy import Column, Integer, String

from weblab.core.coordinator.model import Base, RESERVATION_ID_SIZE

TABLE_KWARGS = get_table_kwargs()

SUFFIX = 'EWLD_' # External WebLab-Deusto

class ExternalWebLabDeustoReservation(Base):
    __tablename__  = SUFFIX + 'ExternalWebLabDeusto'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)

    local_reservation_id             = Column(String(RESERVATION_ID_SIZE))

    # It might come with the cookie value
    remote_reservation_id            = Column(String(RESERVATION_ID_SIZE * 3))

    # In tests, it took up to 726 characters. Just in case, we store more than twice more
    cookies                          = Column(String(1536))

    start_time                       = Column(Integer)

    @typecheck(typecheck.ANY, basestring, basestring, basestring, float)
    def __init__(self, local_reservation_id, remote_reservation_id, cookies, start_time):
        self.local_reservation_id  = local_reservation_id
        self.remote_reservation_id = remote_reservation_id
        self.cookies               = cookies
        self.start_time            = start_time

    def __repr__(self):
        return SUFFIX + "ExternalWebLabDeustoReservation(%r, %r, %r, %r)" % (
                            self.local_reservation_id, self.remote_reservation_id, self.cookies, self.start_time)

class ExternalWeblabDeustoReservationPendingResults(Base):
    __tablename__  = SUFFIX + 'ExternalWebLabDeustoPendingResults'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)
    
    reservation_id     = Column(String(RESERVATION_ID_SIZE))
    resource_type_name = Column(String(255))
   
    def __init__(self, reservation_id, resource_type_name):
        self.reservation_id     = reservation_id
        self.resource_type_name = resource_type_name

    def __repr__(self):
        return SUFFIX + "ExternalWeblabDeustoReservationPendingResults(%r, %r)" % (
                            self.reservation_id, self.resource_type_name)

class ExternalWeblabDeustoReservationProcessingResults(Base):
    __tablename__  = SUFFIX + 'ExternalWebLabDeustoProcessingResults'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)
    
    reservation_id     = Column(String(RESERVATION_ID_SIZE))
    resource_type_name = Column(String(255))
   
    def __init__(self, reservation_id, resource_type_name):
        self.reservation_id     = reservation_id
        self.resource_type_name = resource_type_name

    def __repr__(self):
        return SUFFIX + "ExternalWeblabDeustoReservationProcessingResults(%r, %r)" % (
                            self.reservation_id, self.resource_type_name)

