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

import time

import voodoo.sessions.exc as SessionExceptions

SESSION_LOCKER_MYSQL_HOST = 'session_locker_mysql_host'
DEFAULT_SESSION_LOCKER_MYSQL_HOST = 'localhost' 

SESSION_LOCKER_MYSQL_DB_NAME = 'session_locker_mysql_db_name'
DEFAULT_SESSION_LOCKER_MYSQL_DB_NAME = 'WebLabSessions'

SESSION_LOCKER_MYSQL_USERNAME  = 'session_locker_mysql_username'
SESSION_LOCKER_MYSQL_PASSWORD  = 'session_locker_mysql_password'

I_COULD_LOCK_THE_SESSION = 0
SESSION_ALREADY_ACQUIRED = 1
MAX_TIME_TRYING_TO_LOCK  = 300 # seconds

import MySQLdb as dbi
import sqlalchemy

SESSION_LOCKER_MYSQL_CONNECTION_POOL_SIZE = 'session_locker_mysql_connection_pool_size'
DEFAULT_SESSION_LOCKER_MYSQL_CONNECTION_POOL_SIZE = 25

SESSION_LOCKER_MYSQL_CONNECTION_TIMEOUT = 'session_locker_mysql_connection_timeout'
DEFAULT_SESSION_LOCKER_MYSQL_CONNECTION_TIMEOUT = 60

class DbLocker(object):
    def __init__(self, cfg_manager):
        super(DbLocker, self).__init__()
        self.cfg_manager= cfg_manager

        (
            self.host, 
            self.database_name,
            self.username,
            self.password
        ) = self._parse_config()

        pool_size = cfg_manager.get_value(SESSION_LOCKER_MYSQL_CONNECTION_POOL_SIZE, DEFAULT_SESSION_LOCKER_MYSQL_CONNECTION_POOL_SIZE)
        timeout   = cfg_manager.get_value(SESSION_LOCKER_MYSQL_CONNECTION_TIMEOUT, DEFAULT_SESSION_LOCKER_MYSQL_CONNECTION_TIMEOUT)
        self.dbi  = sqlalchemy.pool.manage(dbi, pool_size = pool_size, timeout = timeout)

    def _parse_config(self):
        host     = self.cfg_manager.get_value(SESSION_LOCKER_MYSQL_HOST, DEFAULT_SESSION_LOCKER_MYSQL_HOST)
        db_name  = self.cfg_manager.get_value(SESSION_LOCKER_MYSQL_DB_NAME, DEFAULT_SESSION_LOCKER_MYSQL_DB_NAME)
        username = self.cfg_manager.get_value(SESSION_LOCKER_MYSQL_USERNAME)
        password = self.cfg_manager.get_value(SESSION_LOCKER_MYSQL_PASSWORD)
        return host, db_name, username, password

    def _get_db_connection(self):
        try:
            return self.dbi.connect(
                host    = self.host,
                user    = self.username,
                passwd  = self.password,
                db      = self.database_name
            )
        except self.dbi.DatabaseError as e:
            raise SessionExceptions.SessionDatabaseConnectionException(
                    "Error connecting to the database %s" % e,
                    e
                )

    def acquire(self, session_id):
        time_to_sleep = 0.1
        number_of_tries = MAX_TIME_TRYING_TO_LOCK / time_to_sleep
        while number_of_tries > 0:
            connection = self._get_db_connection()
            try:
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT wl_LockSession(%s)", session_id)
                    result = cursor.fetchone()
                finally:
                    cursor.close()
            finally:
                connection.commit()
                connection.close()

            if result[0] == I_COULD_LOCK_THE_SESSION:
                return
            elif result[0] == SESSION_ALREADY_ACQUIRED:
                number_of_tries -= 1
                self._wait_time(time_to_sleep)
            else:
                raise SessionExceptions.CouldntAcquireSessionException(
                        "Couldn't acquire session: %s" % result[0]
                    )
        else:
            raise SessionExceptions.SessionAlreadyAcquiredException(
                    "Session already acquired"
                )

    def release(self, session_id):
        connection = self._get_db_connection()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT wl_UnlockSession(%s)", session_id)
                result = cursor.fetchone()
            finally:
                cursor.close()
        finally:
            connection.commit()
            connection.close()

        if result[0] == 0:
            return
        else:
            raise SessionExceptions.CouldntReleaseSessionException(
                    "Couldn't acquire session: %s" % result[0]
                )

    def _wait_time(self, secs):
        time.sleep(secs)

