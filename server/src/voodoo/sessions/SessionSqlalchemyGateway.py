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

import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

import voodoo.sessions.SessionSqlalchemyData as DbData

import voodoo.sessions.SessionGenerator  as SessionGenerator
import voodoo.sessions.SessionSerializer as SessionSerializer
import voodoo.sessions.DbLock            as DbLock

import voodoo.exceptions.sessions.SessionExceptions as SessionExceptions


MAX_TIME_TRYING_TO_LOCK  = 300 # seconds

SESSION_SQLALCHEMY_ENGINE = 'session_sqlalchemy_engine'
DEFAULT_SESSION_SQLALCHEMY_ENGINE = 'mysql' 

SESSION_SQLALCHEMY_HOST = 'session_sqlalchemy_host'
DEFAULT_SESSION_SQLALCHEMY_HOST = 'localhost' 

SESSION_SQLALCHEMY_DB_NAME = 'session_sqlalchemy_db_name'
DEFAULT_SESSION_SQLALCHEMY_DB_NAME = 'WebLabSessions'

SESSION_SQLALCHEMY_USERNAME  = 'session_sqlalchemy_username'
SESSION_SQLALCHEMY_PASSWORD  = 'session_sqlalchemy_password'

def getconn():
    import MySQLdb as dbi
    return dbi.connect(user = SessionSqlalchemyGateway.username, passwd = SessionSqlalchemyGateway.password, 
                        host = SessionSqlalchemyGateway.host, db = SessionSqlalchemyGateway.dbname, client_flag = 2)

class SessionSqlalchemyGateway(object):

    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20)

    def __init__(self, cfg_manager, session_pool_id, timeout):
        super(SessionSqlalchemyGateway, self).__init__()

        self.session_pool_id = session_pool_id
        self.timeout         = timeout
        self.cfg_manager     = cfg_manager

        (
            engine_name,
            host, 
            dbname,
            username,
            password
        ) = self._parse_config()

        SessionSqlalchemyGateway.username = username
        SessionSqlalchemyGateway.password = password
        SessionSqlalchemyGateway.host     = host
        SessionSqlalchemyGateway.dbname = dbname

        self._generator  = SessionGenerator.SessionGenerator()
        self._serializer = SessionSerializer.SessionSerializer()

        self._lock       = DbLock.DbLock(cfg_manager, session_pool_id)

        sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine_name, username, password, host, dbname)
        engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, pool = self.pool)

        self._session_maker = sessionmaker(bind=engine, autoflush = True, autocommit = False)


    def _parse_config(self):
        engine   = self.cfg_manager.get_value(SESSION_SQLALCHEMY_ENGINE, DEFAULT_SESSION_SQLALCHEMY_ENGINE)
        host     = self.cfg_manager.get_value(SESSION_SQLALCHEMY_HOST, DEFAULT_SESSION_SQLALCHEMY_HOST)
        db_name  = self.cfg_manager.get_value(SESSION_SQLALCHEMY_DB_NAME, DEFAULT_SESSION_SQLALCHEMY_DB_NAME)
        username = self.cfg_manager.get_value(SESSION_SQLALCHEMY_USERNAME)
        password = self.cfg_manager.get_value(SESSION_SQLALCHEMY_PASSWORD)
        return engine, host, db_name, username, password


    def create_session(self):

        while True:
            new_id = self._generator.generate_id()
            none_s = self._serializer.serialize({})

            db_session = DbData.Session(new_id, self.session_pool_id, datetime.datetime.now(), none_s)
            session = self._session_maker()
            session.add(db_session)
            try:
                session.commit()
            except IntegrityError, ie:
                continue
            else:
                return new_id
            finally:
                session.close()

    def has_session(self, session_id):
        session = self._session_maker()
        try:
            result = session.query(DbData.Session).filter_by(session_pool_id = self.session_pool_id, sess_id = session_id).first()
            return result is not None
        finally:
            session.close()

    def get_session(self, session_id):
        session = self._session_maker()
        try:
            result = session.query(DbData.Session).filter_by(session_pool_id = self.session_pool_id, sess_id = session_id).first()
            if result is None:
                raise SessionExceptions.SessionNotFoundException( "Session not found: " + session_id )
            session_object = result.session_obj
            result.latest_access = datetime.datetime.now()
            session.commit()
        finally:
            session.close()
        pickled_sess_obj = str(session_object)
        return self._serializer.deserialize(pickled_sess_obj)

    def modify_session(self, sess_id, sess_obj):
        serialized_sess_obj = self._serializer.serialize(sess_obj)

        session = self._session_maker()
        try:
            result = session.query(DbData.Session).filter_by(session_pool_id = self.session_pool_id, sess_id = sess_id).first()
            if result is None:
                raise SessionExceptions.SessionNotFoundException( "Session not found: %s" % sess_id)

            result.session_obj = serialized_sess_obj
            result.latest_access = datetime.datetime.now()
            result.latest_change = result.latest_access

            session.commit()
        finally:
            session.close()

    def get_session_locking(self, session_id):
        self._lock.acquire(session_id)
        try:
            return self.get_session(session_id)
        except:
            self._lock.release(session_id)
            raise

    def modify_session_unlocking(self, sess_id, sess_obj):
        try:
            return self.modify_session(sess_id, sess_obj)
        finally:
            self._lock.release(sess_id)


    def list_sessions(self):
        session = self._session_maker()
        try:
            sessions = session.query(DbData.Session).filter_by(session_pool_id = self.session_pool_id).all()
        finally:
            session.close()
        return [ sess.sess_id for sess in sessions ]

    def clear(self):
        session = self._session_maker()
        try:
            for session_to_delete in session.query(DbData.Session).filter_by(session_pool_id = self.session_pool_id).all():
                session.delete(session_to_delete)
            session.commit()
        finally:
            session.close()

    def delete_expired_sessions(self):
        session = self._session_maker()
        try:
            # NOW() - latest_access > timeout
            # is the same as
            # latest_access > timeout + NOW()
            timeout_datetime = self._get_time() + datetime.timedelta(seconds = (self.timeout / 1000.0))
            for session_to_delete in session.query(DbData.Session).filter(and_(DbData.Session.session_pool_id == self.session_pool_id, DbData.Session.latest_access >  timeout_datetime )).all():
                session.delete(session_to_delete)
            session.commit()
        finally:
            session.close()

    def _get_time(self):
        return datetime.datetime.now()

    def delete_session(self, sess_id):
        session = self._session_maker()
        try:

            result = session.query(DbData.Session).filter_by(session_pool_id = self.session_pool_id, sess_id = sess_id).first()
            if result is None:
                raise SessionExceptions.SessionNotFoundException( "Session not found: %s" % sess_id)

            session.delete(result)
            session.commit()

        except SessionExceptions.SessionNotFoundException:
            raise
        except Exception, e:
            raise SessionExceptions.SessionDatabaseExecutionException( "Database exception retrieving session: %s" % e, e )

    def delete_session_unlocking(self, sess_id):
        try:
            return self.delete_session(sess_id)
        finally:
            self._locker.release(sess_id)

