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

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

SessionLockBase = declarative_base()

class SessionLock(SessionLockBase):
    __tablename__ = 'SessionLocks'

    sess_id        = Column(String(100), primary_key = True)

    def __init__(self, sess_id):
        self.sess_id = sess_id

