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

from voodoo.representable import Representable
from voodoo.typechecker import typecheck
from voodoo.dbutil import get_table_kwargs
from sqlalchemy import Column, Integer, String, Index

from weblab.core.coordinator.sql.model import Base, RESERVATION_ID_SIZE

TABLE_KWARGS = get_table_kwargs()

SUFFIX = 'EWLD_' # External WebLab-Deusto

class ExternalWebLabDeustoReservation(Base):
    __tablename__  = SUFFIX + 'ExternalWebLabDeusto'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)

    local_reservation_id             = Column(String(RESERVATION_ID_SIZE), index = True)

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

class ExternalWebLabDeustoReservationPendingResults(Base):
    __tablename__  = SUFFIX + 'ExternalWebLabDeustoPendingResults'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)
    
    reservation_id        = Column(String(RESERVATION_ID_SIZE), index = True)
    remote_reservation_id = Column(String(RESERVATION_ID_SIZE * 3))
    resource_type_name    = Column(String(255))
    # In order to avoid concurrence among different servers, every sever will know 
    # who stored it and therefore who should retrieve the results
    server_route            = Column(String(255))

    username                = Column(String(255))
    serialized_request_info = Column(String(1536))
    experiment_id_str   = Column(String(255 * 2 + 1))
   
    @typecheck(typecheck.ANY, basestring, basestring, basestring, basestring, basestring, basestring, basestring)
    def __init__(self, reservation_id, remote_reservation_id, resource_type_name, server_route, username, serialized_request_info, experiment_id_str):
        self.reservation_id          = reservation_id
        self.remote_reservation_id   = remote_reservation_id
        self.resource_type_name      = resource_type_name
        self.server_route            = server_route
        self.username                = username
        self.serialized_request_info = serialized_request_info
        self.experiment_id_str       = experiment_id_str

    def __repr__(self):
        return SUFFIX + "ExternalWeblabDeustoReservationPendingResults(%r, %r, %r, %r, %r, %r, %r)" % (
                            self.reservation_id, self.remote_reservation_id, self.resource_type_name, self.server_route, self.username, self.serialized_request_info, self.experiment_id_str)

    def to_dto(self):
        return ExternalWebLabDeustoReservationPendingResultDTO(self.id, self.reservation_id, self.remote_reservation_id, self.username, self.serialized_request_info, self.experiment_id_str)

Index('ix_EWLD_results_reso_route', ExternalWebLabDeustoReservationPendingResults.server_route, ExternalWebLabDeustoReservationPendingResults.resource_type_name)

Index('ix_EWLD_results_reso_route_rese', ExternalWebLabDeustoReservationPendingResults.server_route, ExternalWebLabDeustoReservationPendingResults.resource_type_name, ExternalWebLabDeustoReservationPendingResults.reservation_id)

class ExternalWebLabDeustoReservationPendingResultDTO(object):
    __metaclass__ = Representable

    def __init__(self, id, reservation_id, remote_reservation_id, username, serialized_request_info, experiment_id_str):
        self.id                      = id
        self.reservation_id          = reservation_id
        self.remote_reservation_id   = remote_reservation_id
        self.username                = username
        self.serialized_request_info = serialized_request_info
        self.experiment_id_str       = experiment_id_str

