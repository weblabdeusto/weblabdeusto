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


from sqlalchemy import Column, Integer, String

from weblab.core.coordinator.model import Base, RESERVATION_ID_SIZE

TABLE_KWARGS = {'mysql_engine' : 'InnoDB'}

SUFFIX = 'EWLD_' # External WebLab-Deusto

class ExternalWebLabDeustoReservation(Base):
    __tablename__  = SUFFIX + 'ExternalWebLabDeusto'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)

    local_reservation_id             = Column(String(RESERVATION_ID_SIZE))

    remote_reservation_id            = Column(String(RESERVATION_ID_SIZE * 3)) # It should include the cookie

    start_time                       = Column(Integer)

    def __init__(self, local_reservation_id, remote_reservation_id, start_time):
        self.local_reservation_id  = local_reservation_id
        self.remote_reservation_id = remote_reservation_id
        self.start_time            = start_time

    def __repr__(self):
        return SUFFIX + "ExternalWebLabDeustoReservation(%r, %r, %r)" % (
                            self.local_reservation_id,
                            self.remote_reservation_id,
                            self.start_time
                        )

