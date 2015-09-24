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
import threading
import time
import sys

import weblab.configuration_doc as configuration_doc

import voodoo.sessions.generator as SessionGenerator
import voodoo.sessions.serializer as SessionSerializer
import voodoo.log as log

import voodoo.sessions.exc as SessionErrors

class SessionObj(object):
    def __init__(self, obj):
        self.latest_change = time.time()
        self.latest_access = self.latest_change
        self._obj        = obj

    def get_obj(self):
        self.latest_access = time.time()
        return self._obj

    def set_obj(self, value):
        self.latest_change = time.time()
        self.latest_access = self.latest_change
        self._obj        = value

    obj = property(get_obj, set_obj)

    def is_expired(self, timeout):
        now = time.time()
        seconds = now - self.latest_access
        return seconds > timeout

class SessionMemoryGateway(object):
    def __init__(self, cfg_manager, session_pool_id, timeout):
        # session_pool_id makes no sense in Memory
        object.__init__(self)

        # Using SERIALIZE_MEMORY_GATEWAY_SESSIONS has an impact on performance (it will serialize
        # and deserialize every session everytime), but isolates every session just as if they
        # were stored in the database
        self._serialize     = cfg_manager[configuration_doc.SESSION_MEMORY_GATEWAY_SERIALIZE]

        self._cfg_manager   = cfg_manager
        self._generator     = SessionGenerator.SessionGenerator()
        self._serializer    = SessionSerializer.SessionSerializer()

        self._sessions      = {
                    # First char : (dict_lock, { session_id : session})
                }
        self._session_locks = {
                    # First char : { session_id : session_lock }
                }

        self._timeout         = timeout

        for first_char in self._generator.alphabet:
            self._sessions[first_char] = (threading.RLock(), {})
            self._session_locks[first_char] = {}

    def _get_lock_and_sessions(self, session_id):
        if len(session_id) == 0:
            raise SessionErrors.SessionNotFoundError("Empty session ('')")
        return self._sessions[session_id[:1]]

    def _get_session_lock(self, session_id):
        return self._session_locks[session_id[:1]]

    def delete_expired_sessions(self):
        if self._timeout is None:
            return

        session_ids = self.list_sessions()
        for session_id in session_ids:
            try:
                session_obj = self.get_session_obj(session_id)
                if session_obj.is_expired(self._timeout):
                    self.delete_session(session_id)
            except SessionErrors.SessionNotFoundError:
                # The session was removed during the iteration of this loop
                continue
            except:
                exc, inst, _ = sys.exc_info()
                log.log( self, log.level.Error, "Unexpected exception (%s, %s) while trying to remove session_id %s" % (exc, inst, session_id))
                log.log_exc( self, log.level.Warning )
                continue

    def create_session(self, desired_sess_id=None):
        if desired_sess_id is not None:
            # The user wants a specific session_id
            lock, sessions = self._get_lock_and_sessions(desired_sess_id)
            lock.acquire()
            if desired_sess_id in sessions:
                lock.release()
                raise SessionErrors.DesiredSessionIdAlreadyExistsError("session_id: %s" % desired_sess_id)
            session_id = desired_sess_id

        else:
            # We generate the session_id:
            must_repeat = True
            while must_repeat:
                session_id = self._generator.generate_id()
                lock, sessions = self._get_lock_and_sessions(session_id)
                lock.acquire()
                must_repeat = session_id in sessions
                if must_repeat:
                    lock.release()

        #lock is not released: we're sure that session_id is unique in self.sessions
        if self._serialize:
            obj = self._serializer.serialize({})
        else:
            obj = {}
        sessions[session_id]      = SessionObj(obj)
        # If a single thread calls:
        #  session = get_session_locking(session_id)
        #  something()
        #  modify_session_unlocking(session_id, session)
        #
        # And something() calls again:
        # session = get_session_locking(same_session_id)
        # session['foo'] = 'bar'
        # modify_session_unlocking(same_session_id, session)
        #
        # Then once "something" is called, the first function will store
        # the original session, therefore removing the changes performed
        # in "something". That's really dangerous, so we use here a
        # threading.Lock so the thread is locked and this can't happen.
        self._session_locks[session_id[:1]][session_id] = threading.Lock()
        lock.release()
        return session_id


    def has_session(self, session_id):
        lock, sessions = self._get_lock_and_sessions(session_id)
        with lock:
            return session_id in sessions

    def get_session_obj(self, session_id):
        lock, sessions = self._get_lock_and_sessions(session_id)
        with lock:
            if not session_id in sessions:
                raise SessionErrors.SessionNotFoundError(
                            "Session not found: " + session_id
                        )
            session = sessions[session_id]

        return session

    def get_session(self,session_id):
        session = self.get_session_obj(session_id)

        if self._serialize:
            return self._serializer.deserialize(session.obj)
        else:
            return session.obj

    def modify_session(self,sess_id, sess_obj):
        if self._serialize:
            sess_obj = self._serializer.serialize(sess_obj)
        lock, sessions = self._get_lock_and_sessions(sess_id)
        with lock:
            if not sess_id in sessions:
                raise SessionErrors.SessionNotFoundError(
                            "Session not found: " + sess_id
                        )
            sessions[sess_id] = SessionObj(sess_obj)

    def get_session_locking(self, session_id):
        lock, sessions = self._get_lock_and_sessions(session_id)
        session_locks  = self._get_session_lock(session_id)

        with lock:
            session  = self.get_session(session_id)
            lck      = session_locks[session_id]
            acquired = lck.acquire(False)

        if not acquired:
            lck.acquire()
            session = self.get_session(session_id)

        return session

    def modify_session_unlocking(self, session_id, sess_obj):
        lock, sessions = self._get_lock_and_sessions(session_id)
        session_locks  = self._get_session_lock(session_id)

        with lock:
            try:
                self.modify_session(session_id, sess_obj)
            finally:
                try:
                    session_locks[session_id].release()
                except KeyError:
                    # It has been deleted while modifying. Do nothing.
                    pass

    def unlock_without_modifying(self, session_id):
        lock, sessions = self._get_lock_and_sessions(session_id)
        session_locks  = self._get_session_lock(session_id)

        with lock:
            try:
                session_locks[session_id].release()
            except KeyError:
                # It has been deleted while modifying. Do nothing.
                pass


    def list_sessions(self):
        total_session_ids = []
        for first_chars in self._sessions:
            lock, sessions = self._sessions[first_chars]
            with lock:
                for session_id in sessions:
                    total_session_ids.append(session_id)

        return total_session_ids

    def clear(self):
        """ If calling this method concurrently with a create_session,
        it might happen that in no moment the sessions is empty. """
        for first_chars in self._sessions:
            lock, sessions = self._sessions[first_chars]
            session_locks  = self._session_locks[first_chars]
            with lock:
                sessions.clear()
                session_locks.clear()

    def delete_session(self,session_id):
        lock, sessions = self._get_lock_and_sessions(session_id)
        session_locks  = self._get_session_lock(session_id)

        with lock:
            if session_id in sessions:
                sessions.pop(session_id)
                session_locks.pop(session_id)
            else:
                raise SessionErrors.SessionNotFoundError(
                            "Session not found: " + session_id
                        )

    def delete_session_unlocking(self,session_id):
        lock, sessions = self._get_lock_and_sessions(session_id)
        session_locks  = self._get_session_lock(session_id)

        with lock:
            if session_id in sessions:
                sessions.pop(session_id)
                session_lock = session_locks.pop(session_id)
                session_lock.release()
            else:
                raise SessionErrors.SessionNotFoundError(
                            "Session not found: " + session_id
                        )

