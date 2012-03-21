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
from sqlalchemy import Column, Integer, String

from weblab.core.coordinator.model import Base, RESERVATION_ID_SIZE

TABLE_KWARGS = get_table_kwargs()

SUFFIX = 'ILAB_BATCH_'

class ILabBatchReservation(Base):
    __tablename__  = SUFFIX + 'ILabBatchReservation'
    __table_args__ = TABLE_KWARGS

    id = Column(Integer, primary_key=True)

    local_reservation_id             = Column(String(RESERVATION_ID_SIZE))

    lab_server_url                   = Column(String(255))

    remote_experiment_id            = Column(Integer)

    def __init__(self, local_reservation_id, lab_server_url, remote_experiment_id):
        self.local_reservation_id = local_reservation_id
        self.lab_server_url       = lab_server_url
        self.remote_experiment_id = remote_experiment_id

    def __repr__(self):
        return SUFFIX + "ILabBatchReservation(%r, %r, %r, %r)" % (
                            self.local_reservation_id,
                            self.lab_server_url,
                            self.remote_experiment_id,
                        )

