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

import time
import threading
import weakref

import weblab.configuration_doc as configuration_doc

import voodoo.sessions.session_type as SessionType
import voodoo.sessions.gateway as SessionGateway
import voodoo.sessions.session_id as SessionId

import voodoo.sessions.exc as SessionErrors

DEBUGGING = True

class SessionManagerCleaner(threading.Thread):

    _session_managers = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("SessionManagerCleaner")
        self.stopping = False

    @staticmethod
    def append_session_manager(session_manager):
        SessionManagerCleaner._session_managers.append( weakref.ref( session_manager ) )

    def stop(self):
        self.stopping = True

    def run(self):
        while not self.stopping:
            time.sleep(5)
            try:
                session_managers = SessionManagerCleaner._session_managers[:]
                for session_manager_ref in session_managers:
                    session_manager = session_manager_ref()
                    if session_manager is None:
                        try:
                            SessionManagerCleaner._session_managers.remove(session_manager_ref)
                        except ValueError:
                            pass
                    else:
                        session_manager.delete_expired_sessions()

            except Exception as e:
                if DEBUGGING:
                    print("Error!",e)
                    import traceback
                    traceback.print_exc()

_cleaner = SessionManagerCleaner()
_cleaner.setDaemon(True)
_cleaner.start()

class SessionManager(object):
    def __init__(self,cfg_manager, session_type, session_pool_id, timeout = "default"):
        """ SessionManager(cfg_manager, session_type, session_pool_id[, timeout])

        * cfg_manager: a ConfigurationManager
        * session_type: a SessionType
        * session_pool_id: a str identifying which session pool are we refering to
        * timeout: the timeout of this session_pool_id. It can be an int or a float (both refering to seconds), or None (to set no timeout)
        """
        object.__init__(self)
        if not session_type in SessionType.getSessionTypeValues():
            raise SessionErrors.SessionInvalidSessionTypeError(
                    "Not a session type: %s " % session_type
                )

        self._cfg_manager = cfg_manager
        if timeout == "default":
            timeout = self._cfg_manager.get_doc_value(configuration_doc.SESSION_MANAGER_DEFAULT_TIMEOUT)

        gateway_class = SessionGateway.get_gateway_class(session_type)
        self.gateway = gateway_class(cfg_manager, session_pool_id, timeout)
        self._session_type = session_type

        SessionManagerCleaner.append_session_manager(self)

    @property
    def session_type(self):
        return self._session_type

    def create_session(self, desired_sess_id=None):
        """@param desired_sess_id If given, it's the precise sess_id we want to use as a key to store data in the session_manager."""
        str_sess_id = self.gateway.create_session(desired_sess_id)
        return SessionId.SessionId(str_sess_id)

    def has_session(self, sess_id):
        return self.gateway.has_session(sess_id.id)

    def get_session(self,sess_id):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.get_session(sess_id.id)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def get_session_locking(self, sess_id):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.get_session_locking(sess_id.id)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def modify_session(self,sess_id,sess_obj):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.modify_session(sess_id.id,sess_obj)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def modify_session_unlocking(self,sess_id,sess_obj):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.modify_session_unlocking(sess_id.id,sess_obj)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def unlock_without_modifying(self,sess_id):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.unlock_without_modifying(sess_id.id)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def list_sessions(self):
        return [ SessionId.SessionId(sid) for sid in self.gateway.list_sessions() ]

    def clear(self):
        self.gateway.clear()

    def delete_session(self,sess_id):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.delete_session(sess_id.id)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def delete_session_unlocking(self,sess_id):
        if isinstance(sess_id,SessionId.SessionId):
            return self.gateway.delete_session_unlocking(sess_id.id)
        else:
            raise SessionErrors.SessionInvalidSessionIdError(
                "Not a SessionId: %s " % sess_id
            )

    def delete_expired_sessions(self):
        self.gateway.delete_expired_sessions()
