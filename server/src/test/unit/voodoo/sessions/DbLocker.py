#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import unittest
import pmock

import voodoo.sessions.DbLocker as DbLocker
import voodoo.exceptions.sessions.SessionExceptions as SessionExceptions

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

def _create_connection(cfg_manager, locker):
    host     = cfg_manager.get_value(DbLocker.SESSION_LOCKER_MYSQL_HOST)
    db_name  = cfg_manager.get_value(DbLocker.SESSION_LOCKER_MYSQL_DB_NAME)
    username = cfg_manager.get_value(DbLocker.SESSION_LOCKER_MYSQL_USERNAME)
    password = cfg_manager.get_value(DbLocker.SESSION_LOCKER_MYSQL_PASSWORD)

    return locker.dbi.connect(
            host    = host,
            user    = username,
            passwd  = password,
            db      = db_name
        )

def _create_initial_session(cfg_manager, locker):
    connection = _create_connection(cfg_manager, locker)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT wl_CreateSession(%s, %s, %s)",(SESSION_ID1,"foo","whatever"))
        result = cursor.fetchone()
        if len(result) != 1 or result[0] != 0:
            raise Exception("Invalid result creating session: %s" % result)
        cursor.execute("SELECT wl_CreateSession(%s, %s, %s)",(SESSION_ID2,"foo", "whatever"))
        result = cursor.fetchone()
        if len(result) != 1 or result[0] != 0:
            raise Exception("Invalid result creating session: %s" % result)
    finally:
        cursor.close()
        connection.commit()
        connection.close()

def _remove_sessions(cfg_manager, locker):
    connection = _create_connection(cfg_manager, locker)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM wl_DbSessions")
    cursor.close()
    connection.commit()
    connection.close()

SESSION_ID1 = "mysession1"
SESSION_ID2 = "mysession2"

class WrappedFastDbLocker(DbLocker.DbLocker):
    def __init__(self, *args, **kargs):
        super(WrappedFastDbLocker, self).__init__(*args, **kargs)
    def _wait_time(self, secs):
        pass

class DbLockerTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        


        self.locker = WrappedFastDbLocker(self.cfg_manager)
        _remove_sessions(self.cfg_manager, self.locker)
        _create_initial_session(self.cfg_manager, self.locker)

    def tearDown(self):
        _remove_sessions(self.cfg_manager, self.locker)

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
            SessionExceptions.SessionAlreadyAcquiredException,
            self.locker.acquire,
            SESSION_ID1
        )

    def test_acquire_lock_failing(self):
        self.locker.acquire(SESSION_ID1)
        self.assertRaises(
            SessionExceptions.SessionAlreadyAcquiredException,
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

class WrappedDbLocker(WrappedFastDbLocker):
    def __init__(self, *args, **kargs):
        super(WrappedDbLocker, self).__init__(*args, **kargs)
        self._sql_result = None

    def _get_db_connection(self):
        mocked_cursor = pmock.Mock()
        mocked_cursor.expects(
                pmock.at_least_once()
            ).method('execute')
        mocked_cursor.expects(
                pmock.at_least_once()
            ).close()
        mocked_cursor.expects(
                pmock.at_least_once()
            ).fetchone().will(
                pmock.return_value(
                    self._sql_result
                )
            )

        mocked_connection = pmock.Mock()
        mocked_connection.expects(
                pmock.at_least_once()
            ).cursor().will(
                pmock.return_value(
                    mocked_cursor
                )
            )
        mocked_connection.expects(
                pmock.at_least_once()
            ).commit()
        mocked_connection.expects(
                pmock.at_least_once()
            ).close()
        return mocked_connection

class DbLockerFailingTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        

        self.locker = WrappedDbLocker(self.cfg_manager)
        _remove_sessions(self.cfg_manager, self.locker)
        _create_initial_session(self.cfg_manager, self.locker)

    def tearDown(self):
        _remove_sessions(self.cfg_manager, self.locker)

    def test_acquire_failing(self):
        self.locker._sql_result = (-1,)
        self.assertRaises(
            SessionExceptions.CouldntAcquireSessionException,
            self.locker.acquire,
            SESSION_ID1
        )

    def test_release_failing(self):
        self.locker._sql_result = (-1,)
        self.assertRaises(
            SessionExceptions.CouldntReleaseSessionException,
            self.locker.release,
            SESSION_ID1
        )


def suite():
    return unittest.TestSuite(
        (
            unittest.makeSuite(DbLockerTestCase),
            unittest.makeSuite(DbLockerFailingTestCase),
        )
    )

if __name__ == '__main__':
    unittest.main()

