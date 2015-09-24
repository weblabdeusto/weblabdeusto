#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import unittest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import weblab.configuration_doc as configuration_doc

from voodoo.dbutil import get_sqlite_dbname
import voodoo.sessions.db_lock_data as DbData

import voodoo.sessions.db_lock as DbLock
import voodoo.sessions.exc as SessionErrors

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

def _remove_sessions(cfg_manager):
    engine_name = cfg_manager.get_doc_value(configuration_doc.SESSION_LOCK_SQLALCHEMY_ENGINE)
    host        = cfg_manager.get_doc_value(configuration_doc.SESSION_LOCK_SQLALCHEMY_HOST)
    db_name     = cfg_manager.get_doc_value(configuration_doc.SESSION_LOCK_SQLALCHEMY_DB_NAME)
    username    = cfg_manager.get_doc_value(configuration_doc.SESSION_LOCK_SQLALCHEMY_USERNAME)
    password    = cfg_manager.get_doc_value(configuration_doc.SESSION_LOCK_SQLALCHEMY_PASSWORD)

    if engine_name == 'sqlite':
        sqlalchemy_engine_str = 'sqlite:///%s' % get_sqlite_dbname(db_name)
    else:
        sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine_name, username, password, host, db_name)
    engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False)

    session = sessionmaker(bind=engine, autoflush = True, autocommit = False)()
    for sess in session.query(DbData.SessionLock):
        session.delete(sess)
    session.commit()
    session.close()

SESSION_ID1 = "mysession1"
SESSION_ID2 = "mysession2"

class WrappedFastDbLock(DbLock.DbLock):
    MAX_TIME_TRYING_TO_LOCK=10
    def __init__(self, *args, **kargs):
        super(WrappedFastDbLock, self).__init__(*args, **kargs)
    def _wait_time(self, secs):
        pass

class DbLockTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)



        self.locker = WrappedFastDbLock(self.cfg_manager, "mypool")
        _remove_sessions(self.cfg_manager)

    def test_very_simple_lock(self):
        self.locker.acquire(SESSION_ID1)
        self.locker.release(SESSION_ID1)

    def test_simple_lock(self):
        self.locker.acquire(SESSION_ID1)
        self.locker.release(SESSION_ID1)
        self.locker.acquire(SESSION_ID1)
        self.locker.release(SESSION_ID1)

    def test_lock_failing(self):
        self.locker.acquire(SESSION_ID1)
        self.assertRaises(
            SessionErrors.SessionAlreadyAcquiredError,
            self.locker.acquire,
            SESSION_ID1
        )

    def test_acquire_lock_failing(self):
        self.locker.acquire(SESSION_ID1)
        self.assertRaises(
            SessionErrors.SessionAlreadyAcquiredError,
            self.locker.acquire,
            SESSION_ID1
        )
        self.locker.release(SESSION_ID1)
        self.locker.acquire(SESSION_ID1)
        self.locker.release(SESSION_ID1)

    def test_two_concurrent_locks(self):
        # First way
        self.locker.acquire(SESSION_ID1)
        self.locker.acquire(SESSION_ID2)
        self.locker.release(SESSION_ID1)
        self.locker.release(SESSION_ID2)

        # Second way
        self.locker.acquire(SESSION_ID1)
        self.locker.acquire(SESSION_ID2)
        self.locker.release(SESSION_ID2)
        self.locker.release(SESSION_ID1)

        # There was no problem
        self.locker.acquire(SESSION_ID1)
        self.locker.release(SESSION_ID1)
        self.locker.acquire(SESSION_ID2)
        self.locker.release(SESSION_ID2)

def suite():
    return unittest.makeSuite(DbLockTestCase)

if __name__ == '__main__':
    unittest.main()

