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
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

import voodoo.sessions.DbLockData as DbData

import voodoo.exceptions.sessions.SessionExceptions as SessionExceptions

SESSION_LOCK_SQLALCHEMY_ENGINE = 'session_lock_sqlalchemy_engine'
DEFAULT_SESSION_LOCK_SQLALCHEMY_ENGINE = 'mysql' 

SESSION_LOCK_SQLALCHEMY_HOST = 'session_lock_sqlalchemy_host'
DEFAULT_SESSION_LOCK_SQLALCHEMY_HOST = 'localhost' 

SESSION_LOCK_SQLALCHEMY_DB_NAME = 'session_lock_sqlalchemy_db_name'
DEFAULT_SESSION_LOCK_SQLALCHEMY_DB_NAME = 'WebLabSessions'

SESSION_LOCK_SQLALCHEMY_USERNAME  = 'session_lock_sqlalchemy_username'
SESSION_LOCK_SQLALCHEMY_PASSWORD  = 'session_lock_sqlalchemy_password'

MAX_TIME_TRYING_TO_LOCK  = 120 # seconds

def getconn():
    import MySQLdb as dbi
    return dbi.connect(user = DbLock.username, passwd = DbLock.password, 
                        host = DbLock.host, db = DbLock.dbname, client_flag = 2)


class DbLock(object):

    MAX_TIME_TRYING_TO_LOCK = MAX_TIME_TRYING_TO_LOCK
    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20)

    def __init__(self, cfg_manager, session_pool_id):
        super(DbLock, self).__init__()
        self.cfg_manager = cfg_manager
        self.pool_id     = session_pool_id
        (
            engine_name,
            host, 
            dbname,
            username,
            password
        ) = self._parse_config()

        DbLock.username = username
        DbLock.password = password
        DbLock.host     = host
        DbLock.dbname   = dbname

        sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine_name, username, password, host, dbname)
        engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, pool = self.pool)

        self._session_maker = sessionmaker(bind=engine, autoflush = True, autocommit = False)

    def _parse_config(self):
        engine_name = self.cfg_manager.get_value(SESSION_LOCK_SQLALCHEMY_ENGINE, DEFAULT_SESSION_LOCK_SQLALCHEMY_ENGINE)
        host        = self.cfg_manager.get_value(SESSION_LOCK_SQLALCHEMY_HOST, DEFAULT_SESSION_LOCK_SQLALCHEMY_HOST)
        db_name     = self.cfg_manager.get_value(SESSION_LOCK_SQLALCHEMY_DB_NAME, DEFAULT_SESSION_LOCK_SQLALCHEMY_DB_NAME)
        username    = self.cfg_manager.get_value(SESSION_LOCK_SQLALCHEMY_USERNAME)
        password    = self.cfg_manager.get_value(SESSION_LOCK_SQLALCHEMY_PASSWORD)
        return engine_name, host, db_name, username, password

    def acquire(self, session_id):
        time_to_sleep = 0.1
        number_of_tries = self.MAX_TIME_TRYING_TO_LOCK / time_to_sleep

        while number_of_tries > 0:
            try:
                session = self._session_maker()

                lock = DbData.SessionLock("%s::%s" % (self.pool_id, session_id))
                session.add(lock)

                session.commit()
            except IntegrityError:
                self._wait_time(time_to_sleep)
                number_of_tries -= 1
            else:
                return
            finally:
                session.close()

        raise SessionExceptions.SessionAlreadyAcquiredException( "Session already acquired")

    def release(self, session_id):
        session = self._session_maker()
        try:
            lock = session.query(DbData.SessionLock).filter_by(sess_id="%s::%s" % (self.pool_id, session_id)).first()
            if lock is None:
                raise SessionExceptions.CouldntReleaseSessionException("Couldn't find session id: %s" % session_id)

            session.delete(lock)

            session.commit()
        finally:
            session.close()

    def _wait_time(self, secs):
        time.sleep(secs)

