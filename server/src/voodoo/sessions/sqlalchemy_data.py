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

from sqlalchemy import Column, String, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

SessionBase = declarative_base()

class Session(SessionBase):
    __tablename__  = 'Sessions'

    sess_id         = Column(String(100), primary_key = True)
    session_pool_id = Column(String(100), nullable = False)
    start_date      = Column(DateTime(),  nullable = False)
    latest_access   = Column(DateTime())
    latest_change   = Column(DateTime())
    session_obj     = Column(LargeBinary(), nullable = False)

    def __init__(self, sess_id, session_pool_id, start_date, session_obj):
        self.sess_id         = sess_id
        self.session_pool_id = session_pool_id
        self.start_date      = start_date
        self.session_obj     = session_obj

