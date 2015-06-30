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

from voodoo.sessions import session_id as SessionId
import cPickle as pickle
import voodoo.sessions.exc as SessionErrors
from functools import wraps

def check_session_parameters(parameters):
    def real_check_session_parameters(func):
        @wraps(func)
        def session_parameters_wrapper(self, session, *args, **kargs):
            #TODO: test me
            for i in parameters:
                if not i in session:
                    raise SessionErrors.VariableNotFoundInSessionError(
                            "Variable not found in session: %s" % i
                        )
            return func(self, session, *args, **kargs)
        return session_parameters_wrapper
    return real_check_session_parameters

def check_session(
        exception_to_raise,
        what_session,
        session_manager_field_name = '_session_manager',
        serializable = True,
        cut_session_id = None
    ):
    """ check_session(exception_to_raise,what_session,session_manager_field_name) -> decorator

    The code snippet below:

    @check_session(my.own.exception,"My System")
    def method(self,session, param):
        tell_me = raw_input()
        session["received"] = tell_me

    @check_session(my.own.exception,"My System")
    def method2(self,session):
        print "Received: ", session["received"]

    inside a class that has an attribute called (whatever session_manager_field_name, by default
    '_session_manager') will check if a session_id provided was found in the session_manager. If
    it was found, and it will pass a the session as parameter, whenever the function finishes, it
    will store the end session in the session_manager. If the session was not found, the method
    will not even be called, and an exception of the type (value exception_to_raise) will be
    raised, with a message involving (value of what_session).
    """
    def real_check_session(func):
        @wraps(func)
        def session_checked_wrapper(self, session_id, *args, **kargs):
            # Make it compatible for both SessionId and SessionId.id datatypes
            if isinstance(session_id, basestring):
                session_id = SessionId.SessionId(session_id)

            session_id_str = session_id.id
            if cut_session_id is not None:
                session_id = SessionId.SessionId(session_id_str.split(cut_session_id)[0])

            session_manager = getattr(self, session_manager_field_name)
            if session_manager.has_session(session_id):
                session = session_manager.get_session_locking(session_id)
                if serializable:
                    try:
                        session_orig = pickle.dumps(session)
                    except TypeError:
                        session_orig = None
                try:
                    return_value = func(self, session, *args,**kargs)
                finally:
                    if serializable:
                        try:
                            session_cur = pickle.dumps(session)
                            modified = session_orig == None or session_orig != session_cur
                        except TypeError:
                            modified = True
                    else:
                        modified = True

                    if modified:
                        session_manager.modify_session_unlocking( session_id, session )
                    else:
                        session_manager.unlock_without_modifying( session_id )
                return return_value
            else:
                raise exception_to_raise(
                    what_session + " session not found"
                )

        return session_checked_wrapper
    return real_check_session


