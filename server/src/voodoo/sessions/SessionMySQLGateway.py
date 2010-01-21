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

import sqlalchemy
import voodoo.sessions.SessionGenerator  as SessionGenerator
import voodoo.sessions.SessionSerializer as SessionSerializer
import voodoo.sessions.DbLocker          as DbLocker

import voodoo.log as log

import voodoo.exceptions.sessions.SessionExceptions as SessionExceptions

SESSION_MYSQL_HOST = 'session_mysql_host'
DEFAULT_SESSION_MYSQL_HOST = 'localhost' 

SESSION_MYSQL_DB_NAME = 'session_mysql_db_name'
DEFAULT_SESSION_MYSQL_DB_NAME = 'WebLabSessions'

SESSION_MYSQL_USERNAME  = 'session_mysql_username'
SESSION_MYSQL_PASSWORD  = 'session_mysql_password'

MYSQL_DB_DRIVER         = 'MySQLdb'

SESSION_MYSQL_CONNECTION_POOL_SIZE = 'session_mysql_connection_pool_size'
DEFAULT_SESSION_MYSQL_CONNECTION_POOL_SIZE = 25

SESSION_MYSQL_CONNECTION_TIMEOUT = 'session_mysql_connection_timeout'
DEFAULT_SESSION_MYSQL_CONNECTION_TIMEOUT = 60

class SessionMySQLGateway(object):
    def __init__(self, cfg_manager, session_pool_id, timeout):
        object.__init__(self)

        self.session_pool_id = session_pool_id
        self.timeout         = timeout
        self.driver          = MYSQL_DB_DRIVER
        self.cfg_manager= cfg_manager
        (
            self.host, 
            self.database_name,
            self.username,
            self.password
        ) = self._parse_config()

        #Module
        self.dbi = __import__(self.driver)

        if sqlalchemy.pool.proxies.has_key(self.dbi):
            log.log( SessionMySQLGateway, log.LogLevel.Warning, "Database already pooled. SessionMySQLGateway configuration of the pool not used" )
        else:
            pool_size          = cfg_manager.get_value(SESSION_MYSQL_CONNECTION_POOL_SIZE, DEFAULT_SESSION_MYSQL_CONNECTION_POOL_SIZE)
            connection_timeout = cfg_manager.get_value(SESSION_MYSQL_CONNECTION_TIMEOUT,   DEFAULT_SESSION_MYSQL_CONNECTION_TIMEOUT)
            self.dbi           = sqlalchemy.pool.manage(self.dbi, pool_size = pool_size, timeout = connection_timeout)

        self.locker = DbLocker.DbLocker(self.cfg_manager)

        self._generator  = SessionGenerator.SessionGenerator()
        self._serializer = SessionSerializer.SessionSerializer()

    def _parse_config(self):
        host     = self.cfg_manager.get_value(SESSION_MYSQL_HOST, DEFAULT_SESSION_MYSQL_HOST)
        db_name  = self.cfg_manager.get_value(SESSION_MYSQL_DB_NAME, DEFAULT_SESSION_MYSQL_DB_NAME)
        username = self.cfg_manager.get_value(SESSION_MYSQL_USERNAME)
        password = self.cfg_manager.get_value(SESSION_MYSQL_PASSWORD)
        return host, db_name, username, password

    def _get_db_connection(self):
        try:
            db_connection = self.dbi.connect(
                    host    = self.host,
                    user    = self.username,
                    passwd  = self.password,
                    db      = self.database_name
                )
            return db_connection
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseConnectionException(
                    "Error connecting to the database %s" % e,
                    e
                )
    
    def create_session(self):
        keep_trying = True
        while keep_trying:
            db_connection = self._get_db_connection()
            cursor = db_connection.cursor()

            new_id = self._generator.generate_id()
            none_s = self._serializer.serialize({})
            try:
                cursor.execute('SELECT wl_CreateSession(%s,%s,%s)',(new_id,self.session_pool_id,none_s))
                result = cursor.fetchone()
                db_connection.commit()
                cursor.close()
                db_connection.close()
            except self.dbi.DatabaseError,e:
                raise SessionExceptions.SessionDatabaseExecutionException(
                        "Database exception creating session: %s" % e,
                        e
                )
            if result[0] == 0:
                keep_trying = False
            elif result[0] != 1:
                raise SessionExceptions.SessionDatabaseException(
                        "Unexpected database error creating session (Returned " + str(result[0]) + ")"
                    )
        return new_id

    def has_session(self,session_id):
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
        try:
            cursor.execute(
                    "SELECT session_id " +
                    "FROM wl_DbSessions " +
                    "WHERE session_id = %s",
                    session_id
                )
            rows = len(cursor.fetchall())
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseExecutionException(
                    "Database exception checking if there was a session: %s" % e,
                    e
                )
        return rows == 1
    
    def get_session(self,session_id):
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
        
        try:
            cursor.execute(
                    "SELECT session_id " +
                    "FROM wl_DbSessions " +
                    "WHERE session_id = %s",
                    session_id
                )
            rows = len(cursor.fetchall())
            if rows == 1:
                cursor.execute(
                    "UPDATE wl_rw_DbSessions " +
                    "SET latest_access = NOW() " +
                    "WHERE session_id = %s ", session_id
                )
                db_connection.commit()
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseExecutionException(
                    "Database exception retrieving session: %s" % e,
                    e
                )

        if rows == 0:
            raise SessionExceptions.SessionNotFoundException(
                    "Session not found: " + session_id
                )
        elif rows != 1:
            raise SessionExceptions.SessionDatabaseException(
                    "Unexpected database error retrieving session"
                )

        try:
            cursor.execute(
                "SELECT session_obj " +
                "FROM wl_DbSessions " +
                "WHERE session_id = %s", session_id
            )
            sess_obj = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseExecutionException(
                    "Database exception retrieving session: %s" % e,
                    e
                )

        if not isinstance(sess_obj,basestring):
            sess_obj = sess_obj.tostring()
        return self._serializer.deserialize(sess_obj)

    def get_session_locking(self, sess_id):
        self.locker.acquire(sess_id)
        try:
            return self.get_session(sess_id)
        except:
            self.locker.release(sess_id)
            raise

    def modify_session_unlocking(self, sess_id, sess_obj):
        try:
            return_value = self.modify_session(sess_id, sess_obj)
        finally:
            self.locker.release(sess_id)
        return return_value

    def modify_session(self,sess_id,sess_obj):
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
        
        serialized_sess_obj = self._serializer.serialize(sess_obj)
        try:
            cursor.execute(
                    "SELECT session_id " +
                    "FROM wl_DbSessions " +
                    "WHERE session_id = %s",
                    sess_id
                )
            rows = len(cursor.fetchall())
        
            if rows == 1:
                cursor.execute(
                    "UPDATE wl_rw_DbSessions " +
                    "SET session_obj = %s " +
                    "WHERE session_id = %s ", 
                    (
                        serialized_sess_obj,
                        sess_id
                    )
                )
                db_connection.commit()
            cursor.close()
            db_connection.close()
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseExecutionException(
                    "Database exception retrieving session: %s" % e,
                    e
                )

        if rows == 0:
            raise SessionExceptions.SessionNotFoundException(
                    "Session not found: %s" % sess_id
                )
        elif rows != 1:
            raise SessionExceptions.SessionDatabaseException(
                    "Unexpected database error retrieving session"
                )
    
    def list_sessions(self):
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
        
        try:
            cursor.execute(
                    "SELECT session_id " +
                    "FROM wl_DbSessions " +
                    "WHERE session_pool_id = %s",
                    self.session_pool_id
                )
            rows = cursor.fetchall()
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseExecutionException(
                    "Database exception retrieving session_ids: %s" % e,
                    e
                )
        return [ row[0] for row in rows ]

    def clear(self):
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
    
        try:
            try:
                cursor.execute(
                        "DELETE FROM wl_DbSessions WHERE session_pool_id = %s",
                        self.session_pool_id
                    )
                db_connection.commit()
            except self.dbi.DatabaseError,e:
                raise SessionExceptions.SessionDatabaseExecutionException(
                        "Database exception clearing sessions" % e,
                        e
                    )
        finally:
            cursor.close()
            db_connection.close()

    def delete_expired_sessions(self):
        if self.timeout is None:
            return
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
    
        try:
            try:
                cursor.execute(
                        "DELETE FROM wl_DbSessions WHERE session_pool_id = %s AND NOW() - latest_access > %s",
                        ( self.session_pool_id, self.timeout )
                    )
                db_connection.commit()
            except self.dbi.DatabaseError,e:
                raise SessionExceptions.SessionDatabaseExecutionException(
                        "Database exception clearing expired sessions" % e,
                        e
                    )
        finally:
            cursor.close()
            db_connection.close()

    def delete_session(self,sess_id):
        db_connection = self._get_db_connection()
        cursor = db_connection.cursor()
        
        try:
            cursor.execute(
                    "SELECT session_id " +
                    "FROM wl_DbSessions " +
                    "WHERE session_id = %s",
                    sess_id
                )
            rows = len(cursor.fetchall())

            if rows == 1:
                cursor.execute(
                    "DELETE FROM wl_DbSessions " +
                    "WHERE session_id = %s ", 
                    sess_id
                )
                db_connection.commit()
            cursor.close()
            db_connection.close()
        except self.dbi.DatabaseError,e:
            raise SessionExceptions.SessionDatabaseExecutionException(
                    "Database exception retrieving session: %s" % e,
                    e
                )

        if rows == 0:
            raise SessionExceptions.SessionNotFoundException(
                    "Session not found: %s" % sess_id
                )
        elif rows != 1:
            raise SessionExceptions.SessionDatabaseException(
                    "Unexpected database error retrieving session"
                )

    def delete_session_unlocking(self, sess_id):
        try:
            return self.delete_session(sess_id)
        finally:
            self.locker.release(sess_id)

