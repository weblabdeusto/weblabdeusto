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

import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

import weblab.configuration_doc as configuration_doc

from voodoo.dbutil import generate_getconn, get_sqlite_dbname
import voodoo.sessions.sqlalchemy_data as DbData

import voodoo.sessions.generator  as SessionGenerator
import voodoo.sessions.serializer as SessionSerializer
import voodoo.sessions.db_lock            as DbLock

import voodoo.sessions.exc as SessionErrors


MAX_TIME_TRYING_TO_LOCK  = 300 # seconds

class SessionSqlalchemyGateway(object):

    engine = None

    def __init__(self, cfg_manager, session_pool_id, timeout):
        super(SessionSqlalchemyGateway, self).__init__()

        self.session_pool_id = session_pool_id
        self.timeout         = timeout
        self.cfg_manager     = cfg_manager

        (
            engine_name,
            host,
            port,
            dbname,
            username,
            password
        ) = self._parse_config()

        SessionSqlalchemyGateway.username = username
        SessionSqlalchemyGateway.password = password
        SessionSqlalchemyGateway.host     = host
        SessionSqlalchemyGateway.port     = port
        SessionSqlalchemyGateway.dbname = dbname

        self._generator  = SessionGenerator.SessionGenerator()
        self._serializer = SessionSerializer.SessionSerializer()

        self._lock       = DbLock.DbLock(cfg_manager, session_pool_id)

        if SessionSqlalchemyGateway.engine is None:
            getconn = generate_getconn(engine_name, username, password, host, port, dbname)

            if engine_name == 'sqlite':
                sqlalchemy_engine_str = 'sqlite:///%s' % get_sqlite_dbname(dbname)
                pool = sqlalchemy.pool.NullPool(getconn)
            else:
                if port is None:
                    port_str = ''
                else:
                    port_str = ':%s' % port
                sqlalchemy_engine_str = "%s://%s:%s@%s%s/%s" % (engine_name, username, password, host, port_str, dbname)
                pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20, recycle=3600)

            SessionSqlalchemyGateway.engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, pool = pool)

        self._session_maker = sessionmaker(bind=self.engine, autoflush = True, autocommit = False)


    def _parse_config(self):
        engine   = self.cfg_manager.get_doc_value(configuration_doc.SESSION_SQLALCHEMY_ENGINE)
        host     = self.cfg_manager.get_doc_value(configuration_doc.SESSION_SQLALCHEMY_HOST)
        port     = self.cfg_manager.get_doc_value(configuration_doc.SESSION_SQLALCHEMY_PORT)
        db_name  = self.cfg_manager.get_doc_value(configuration_doc.SESSION_SQLALCHEMY_DB_NAME)
        username = self.cfg_manager.get_doc_value(configuration_doc.SESSION_SQLALCHEMY_USERNAME)
        password = self.cfg_manager.get_doc_value(configuration_doc.SESSION_SQLALCHEMY_PASSWORD)
        return engine, host, port, db_name, username, password


    def create_session(self, desired_sess_id=None):
        if desired_sess_id is not None:
            # The user wants a specific session_id
            if self.has_session(desired_sess_id):
                raise SessionErrors.DesiredSessionIdAlreadyExistsError("session_id: %s" % desired_sess_id)
            new_id = desired_sess_id
        else:
            new_id = self._generator.generate_id()

        while True:
            none_s = self._serializer.serialize({})

            db_session = DbData.Session(new_id, self.session_pool_id, datetime.datetime.now(), none_s)
            session = self._session_maker()
            session.add(db_session)
            try:
                session.commit()
            except IntegrityError:
                new_id = self._generator.generate_id()
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
                raise SessionErrors.SessionNotFoundError( "Session not found: " + session_id )
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
                raise SessionErrors.SessionNotFoundError( "Session not found: %s" % sess_id)

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

    def unlock_without_modifying(self, sess_id):
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
        if self.timeout is None:
            return

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
                raise SessionErrors.SessionNotFoundError( "Session not found: %s" % sess_id)

            session.delete(result)
            session.commit()

        except SessionErrors.SessionNotFoundError:
            raise
        except Exception as e:
            raise SessionErrors.SessionDatabaseExecutionError( "Database exception retrieving session: %s" % e, e )

    def delete_session_unlocking(self, sess_id):
        try:
            return self.delete_session(sess_id)
        finally:
            self._locker.release(sess_id)

