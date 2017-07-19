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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function

import telnetlib
import traceback
from functools import wraps
import cPickle as pickle

def _raise_exception(e):
    raise pickle.loads(e)

class monitor_method(object):
    """Makes it easy to call the decorated method.

    Example:

    @monitor_method
    def func(a):
        if a == 5:
            return "ok"
        raise Exception("there was an error!")

    retrieved1 = repr(func(pickle.dumps((5,),{})))
    retrieved2 = repr(func(pickle.dumps((10,),{})))
    # repr because in Monitor, it will send that string to the client

    sol1    = handle_response(retrieved1)
    # sol1 is now "ok"
    sol2    = handle_response(retrieved2)
    # an exception of type Exception with parameter "there was an error" is thrown
    """
    def __init__(self, func):
        self._func = func

    ####################
    # Only for testing!
    def call(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def __call__(self, pickled_arg):
        args, kwargs = pickle.loads(pickled_arg)
        try:
            result = self._func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc(file=open('errors.txt','w'))
            return "_raise_exception(%s)" % repr(pickle.dumps(e))
        else:
            return repr(pickle.dumps(result))

def handle_response(response):
    return pickle.loads(eval(eval(response)))

def connected_method(func):
    """ connects before the method and disconnects after it """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.connect()
        try:
            return func(self, *args, **kwargs)
        finally:
            self.disconnect()
    return wrapper

class WebLabShell(object):

    def __init__(self, address, port):
        super(WebLabShell, self).__init__()
        self.address = address
        self.port = port

    def _to_str(self, u):
        if isinstance(u, unicode):
            return u.encode('utf-8')
        return u

    def send(self, command):
        command = self._to_str(command)
        self.telnet.write(command+"\n")
        self._receive()

    def _receive(self):
        return self.telnet.read_until(">>> ")

    def send_and_receive(self, command, *args, **kwargs):
        command = self._to_str(command)
        pickled_args = pickle.dumps((args, kwargs))
        self.telnet.write(command + "(%s)" % repr(pickled_args) + "\n")
        response = self._receive()[:-(len(">>> ") + len("\r\n"))]
        return handle_response(response)

    def _create_telnet(self):
        return telnetlib.Telnet(self.address, int(self.port))

    def connect(self):
        try:
            self.telnet = self._create_telnet()
            self._receive()
            self.send("from weblab.admin.monitor.monitor_methods import *")
        except Exception:
            raise

    def disconnect(self):
        self.telnet.close()

    @connected_method
    def kickout_from_ups(self, session_id):
        return self.send_and_receive("kickout_from_ups", session_id)

    @connected_method
    def get_experiment_ups_session_ids(self, category, experiment):
        return self.send_and_receive("get_experiment_ups_session_ids", category, experiment)

    @connected_method
    def list_all_users(self):
        return self.send_and_receive("list_all_users")

    @connected_method
    def get_reservation_id(self, ups_session_id):
        return self.send_and_receive("get_reservation_id", ups_session_id)

    @connected_method
    def get_ups_session_ids_from_username(self, login):
        return self.send_and_receive("get_ups_session_ids_from_username", login)

    @connected_method
    def list_experiments(self):
        return self.send_and_receive("list_experiments")

    @connected_method
    def get_experiment_status(self, category, experiment):
        return self.send_and_receive("get_experiment_status",category,experiment)

    @connected_method
    def kickout_from_coordinator(self, reservation_id):
        return self.send_and_receive("kickout_from_coordinator", reservation_id)


class WebLabMonitor(object):
    def __init__(self, (ups_ip, ups_port)):
        super(WebLabMonitor, self).__init__()
        self._shell = WebLabShell(ups_ip, ups_port)

    def list_experiments(self):
        return self._shell.list_experiments()

    def list_users(self, full_experiment):
        if full_experiment.find("@") != -1:
            experiment, category = full_experiment.split("@")
            users_status = self._shell.get_experiment_status(category, experiment)
            ups_session_ids = self._shell.get_experiment_ups_session_ids(category, experiment)

            ups_orphans = []
            information = []
            for ups_session_id, login, wlc_session_id in ups_session_ids:
                if wlc_session_id in users_status:
                    status = users_status.pop(wlc_session_id)
                    information.append((login, status, ups_session_id, wlc_session_id))
                else:
                    ups_orphans.append((ups_session_id, login, wlc_session_id))
            wlc_orphans = [ (key, users_status[key]) for key in users_status ]
            return information, ups_orphans, wlc_orphans
        else:
            raise Exception("Invalid experiment name (experiment@category?):", full_experiment)

    def list_all_users(self):
        return self._shell.list_all_users()

    def kick_session(self, ups_session_id):
        try:
            reservation_id = self._shell.get_reservation_id(ups_session_id)
        except Exception as e:
            print("Error retrieving wlc_session_id; skipping... %s" % e)
            return

        try:
            self._shell.kickout_from_ups(ups_session_id)
        except Exception as e:
            if not str(e).startswith("invalid syntax"):
                print(e)
            # It's normal that the server generates some kind of
            # "print" which is redirected here and gets a SyntaxError

        if reservation_id != None:
            try:
                self._shell.kickout_from_coordinator(reservation_id)
            except Exception as e:
                if not str(e).startswith("invalid syntax"):
                    print(e)
                # It's normal that the server generates some kind of
                # "print" which is redirected here and gets a SyntaxError

    def kick_user(self, username):
        ups_session_ids = self._shell.get_ups_session_ids_from_username(username)
        exceptions = []
        for ups_session_id in ups_session_ids:
            try:
                self.kick_session(ups_session_id.id)
            except Exception as e:
                exceptions.append(e)
        if len(exceptions) > 0:
            raise Exception("The following exceptions took place: %s " % repr(exceptions))

