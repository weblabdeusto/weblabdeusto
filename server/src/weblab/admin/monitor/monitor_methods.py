#!/usr/bin/env python
#-*-*- coding: utf-8 -*-*-
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

#
# Here are all the methods that the Monitor will call. The point is
# that instead of doing nasty code in strings inside the Monitor class
# we can write this methods with variables, loops, and so on, and the
# Monitor will call them serializing the result with pickle, so we
# don't need to parse Python code, etc.
#

from weblab.data.dto.users import User
from weblab.data.dto.users import Role
from weblab.admin.monitor.monitor import monitor_method
from weblab.core.server import UserProcessingServer

from weblab.data.experiments import ExperimentId
import voodoo.sessions.exc as SessionErrors

from voodoo.sessions.session_id import SessionId
from voodoo.gen.registry import GLOBAL_REGISTRY
import sys

#
# We take these values when the application is started. Later,
# when replaced, we still use the original ones.
#
stdout = sys.stdout
stderr = sys.stderr
stdin  = sys.stdin

def _find_server(server_type, name):
    servers = []
    for server in GLOBAL_REGISTRY:
        if isinstance(GLOBAL_REGISTRY[server], server_type):
            servers.append(GLOBAL_REGISTRY[server])
    if len(servers) > 1:
        print("Warning: more than one server of %s found" % name, file=stderr)
    elif len(servers) == 0:
        raise Exception("Could not find a %s server" % name)
    return servers[0]

def _find_ups():
    return _find_server(UserProcessingServer, "User Processing")

@monitor_method
def list_experiments():
    ups = _find_ups()
    experiments_by_category = ""
    for exp_id in ups._coordinator.list_experiments():
        experiments_by_category += "%s@%s\n" % (exp_id.exp_name, exp_id.cat_name)
    return experiments_by_category

@monitor_method
def get_experiment_status(category, experiment):
    #
    # Returns a dictionary of reservation_id: weblab.core.coordinator.WebLabQueueSessions.* objects
    #
    ups = _find_ups()
    return ups._coordinator.list_sessions(ExperimentId(experiment, category))

@monitor_method
def get_experiment_ups_session_ids(category, experiment):
    ups = _find_ups()

    user_session_mgr   = ups._session_manager
    session_mgr        = ups._alive_users_collection._session_manager
    users_session_mgr  = ups._alive_users_collection._users_session_manager
    global_sid         = ups._alive_users_collection._experiments_server_session_id

    global_sobj = users_session_mgr.get_session(global_sid)

    return_value = []
    for session_id in global_sobj:
        session_obj = session_mgr.get_session(session_id)
        current_exp = session_obj['experiment_id']
        if current_exp.exp_name == experiment and current_exp.cat_name == category:
            creator_session_id = session_obj['creator_session_id']
            user_session_obj = user_session_mgr.get_session(creator_session_id)
            login  = user_session_obj['user_information'].login
            reservation_id = session_obj['reservation_id']
            return_value.append((session_id.id, login, reservation_id))
    return return_value

@monitor_method
def list_all_users():
    ups = _find_ups()

    session_mgr = ups._session_manager
    session_ids = session_mgr.list_sessions()
    global_sid  = ups._alive_users_collection._experiments_server_session_id

    sessions = []
    for session_id in session_ids:
        if session_id == global_sid:
            continue
        try:
            session = session_mgr.get_session(session_id)
        except SessionErrors.SessionError:
            continue
        if 'user_information' in session:
            user_info = session['user_information']
        else:
            # It may happen if we list the experiments before gathering this information
            user_info = User('<unknown>', '<unknown>', '<unknown>', Role("student"))
        last = session.get('latest_timestamp') or 0
        sessions.append((session_id, user_info, last))
    return sessions

@monitor_method
def get_ups_session_ids_from_username(login):
    ups = _find_ups()
    session_mgr = ups._session_manager
    session_ids = session_mgr.list_sessions()

    global_sid  = ups._alive_users_collection._experiments_server_session_id

    ups_session_ids = []
    for session_id in session_ids:
        if session_id == global_sid:
            continue
        try:
            session = session_mgr.get_session(session_id)
        except SessionErrors.SessionError:
            continue

        if 'user_information' in session:
            if session['user_information'].login == login:
                ups_session_ids.append(session_id)
    return ups_session_ids

@monitor_method
def kickout_from_coordinator(reservation_id):
    ups = _find_ups()
    ups._coordinator.finish_reservation(reservation_id)

@monitor_method
def get_reservation_id(ups_session_id):
    ups = _find_ups()
    sid = SessionId(ups_session_id)
    session = ups._session_manager.get_session(sid)
    return session.get('reservation_id')

@monitor_method
def kickout_from_ups(session_id):
    ups = _find_ups()
    sid = SessionId(session_id)
    ups._alive_users_collection.remove_user(sid.id)
    ups._session_manager.delete_session(sid)


