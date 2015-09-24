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
from __future__ import print_function, unicode_literals

import time
import traceback
import urllib2
from functools import wraps
import json

import cookielib

import voodoo.sessions.session_id as SessionId
import weblab.core.reservations as Reservation
from weblab.core.new_server import simplify_response
import weblab.data.command as Command
from weblab.data.dto.experiments import Experiment, ExperimentClient, ExperimentCategory
from weblab.data.dto.users import User

from exc import InvalidUserOrPasswordError
from exc import ListOfExperimentsIsEmptyError

class Call(object):

    def __init__(self, begin, end, method, args, kargs, return_value, (exception, trace)):
        super(Call, self).__init__()
        self.begin = begin
        self.end = end
        self.method = method
        self.args = args
        self.kargs = kargs
        self.return_value = return_value
        self.exception = (exception, trace)

    def time(self):
        return self.end - self.begin

    def get_exception(self):
        return self.exception

    def __str__(self):
        text = "@call: %s in %s sec, from %s to %s\n" % (self.method, self.time(), self.begin, self.end)
        text += "   args ......: %s\n" % str(self.args)
        text += "   kargs .....: %s\n" % str(self.kargs)
        text += "   return ....: %s\n" % self.return_value
        text += "   exception .: %s"   % str(self.exception[0])
        return text


def logged(func):
    @wraps(func)
    def wrapper(self, *args, **kargs):
        try:
            begin = time.time()
            try:
                return_value = func(self, *args, **kargs)
            except Exception as e:
                return_value = None
                exception_and_trace_raised = (e, traceback.format_exc())
                if self.raise_exceptions:
                    raise
            else:
                exception_and_trace_raised = (None, None)
                return return_value
        finally:
            end = time.time()
            self._add_call(begin, end, func.__name__.lstrip("do_"), args, kargs, return_value, exception_and_trace_raised)

    return wrapper

def possibleKeyError(func):
    @wraps(func)
    def wrapper(self, *args, **kargs):
        try:
            return func(self, *args, **kargs)
        except KeyError:
            raise Exception("Unexpected response in method %s with args %s and kargs %s" % (func.__name__, str(args), str(kargs)) )

    return wrapper

class AbstractBot(object):
    def __init__(self, url, url_login):
        super(AbstractBot, self).__init__()
        self.session_id = ""
        self.calls = []
        self.begin = 0
        self.end = 0
        self.url = url
        self.url_login = url_login
        self.remote_url            = None
        self.remote_reservation_id = None
        self.raise_exceptions      = False

    def _add_call(self, begin, end, method, args, kargs, return_value, (exception, trace)):
        self.calls.append(Call(begin, end, method, args, kargs, return_value, (exception, trace)))

    def start(self):
        self.begin = time.time()

    def finish(self):
        self.end = time.time()
        self.dispose()

    def dispose(self):
        pass # Overrided

    def time(self):
        return self.end - self.begin

    def get_number_of_exceptions(self):
        return len([ call.get_exception() for call in self.calls if call.get_exception() != (None, None) ])

    def get_exceptions(self):
        return [ call.get_exception() for call in self.calls if call.get_exception() != (None, None) ]

    def get_calls(self):
        return self.calls[:]

    def get_calls_by_name(self):
        by_name = {}

        for call in self.calls:
            if call.method in by_name:
                by_name[call.method].append(call)
            else:
                by_name[call.method] = [call]
        return by_name

    def get_log(self):
        text = "\n*** Bot ***\n"
        for call in self.calls:
            text += "\n" + str(call) + "\n"
        return text

    @logged
    def do_login(self, username, password):
        session_holder = self._call('login',username=username, password=password)
        self.session_id = self._parse_session_id(session_holder)
        if self.session_id is not None:
            return self.session_id
        else:
            raise InvalidUserOrPasswordError("Unable to login with username=%s and password=%s" % (self.username, self.password))

    @logged
    def do_list_experiments(self):
        experiment_list_holders = self._call('list_experiments',session_id=self.session_id)
        experiments = self._parse_experiment_list_holders(experiment_list_holders)
        if len(experiments) > 0:
            return experiments
        else:
            raise ListOfExperimentsIsEmptyError("Received list of experiments is empty")

    @logged
    def do_reserve_experiment(self, experiment_id, client_initial_data, consumer_data):
        reservation_holder = self._call('reserve_experiment',session_id=self.session_id, experiment_id=experiment_id, client_initial_data=client_initial_data, consumer_data=consumer_data)
        reservation = self._parse_reservation_holder(reservation_holder)
        if isinstance(reservation, Reservation.ConfirmedReservation) and reservation.remote_reservation_id is not None and reservation.remote_reservation_id != '':
            self.remote_url            = reservation.url
            self.remote_reservation_id = reservation.remote_reservation_id
        else:
            self.remote_url            = None
            self.remote_reservation_id = None
        self.reservation_id = reservation.reservation_id
        return reservation

    @logged
    def do_get_reservation_status(self):
        reservation_holder = self._call('get_reservation_status',reservation_id=self.reservation_id)
        reservation = self._parse_reservation_holder(reservation_holder)
        if isinstance(reservation, Reservation.ConfirmedReservation) and reservation.remote_reservation_id is not None and reservation.remote_reservation_id != '':
            self.remote_url            = reservation.url
            self.remote_reservation_id = reservation.remote_reservation_id
        else:
            self.remote_url            = None
            self.remote_reservation_id = None
        return reservation

    @logged
    def do_logout(self):
        return self._call('logout',session_id=self.session_id)

    @logged
    def do_finished_experiment(self):
        return self._call('finished_experiment',reservation_id=self.reservation_id)

    @logged
    def do_send_file(self, structure, file_info):
        reservation_id = self.remote_reservation_id if self.remote_reservation_id is not None else self.reservation_id
        command_holder = self._call('send_file',reservation_id=reservation_id, file_content=structure, file_info=file_info)
        command = self._parse_command(command_holder)
        return command

    @logged
    def do_send_command(self, command):
        reservation_id = self.remote_reservation_id if self.remote_reservation_id is not None else self.reservation_id
        command_holder = self._call('send_command',reservation_id=reservation_id, command=command)
        command = self._parse_command(command_holder)
        return command

    @logged
    def do_poll(self):
        reservation_id = self.remote_reservation_id if self.remote_reservation_id is not None else self.reservation_id
        return self._call('poll',reservation_id=reservation_id)

    @logged
    def do_get_user_information(self):
        holder = self._call('get_user_information', session_id=self.session_id)
        return self._parse_user(holder)

    @logged
    def do_get_user_permissions(self):
        holder = self._call('get_user_permissions', session_id=self.session_id)
        return self._parse_user(holder)

class AbstractBotDict(AbstractBot):

    def __init__(self, url, url_login):
        super(AbstractBotDict, self).__init__(url, url_login)

    def _parse_session_id(self, session_holder):
        return SessionId.SessionId(session_holder['id'])

    @possibleKeyError
    def _parse_experiment_list_holders(self, experiment_list_holders):
        experiments = []
        for experiment in [ holder['experiment'] for holder in experiment_list_holders]:
            category = ExperimentCategory(experiment['category']['name'])
            client = ExperimentClient(experiment['client']['client_id'], experiment['client']['configuration'])
            exp = Experiment(experiment['name'], category, experiment['start_date'], experiment['end_date'], client)
            experiments.append(exp)
        return experiments

    @possibleKeyError
    def _parse_reservation_holder(self, reservation_holder):
        if reservation_holder.get('remote_reservation_id') is None:
            remote_reservation_id = None
        else:
            remote_reservation_id = reservation_holder.get('remote_reservation_id').get('id')
        return Reservation.Reservation.translate_reservation_from_data(reservation_holder['status'], reservation_holder['reservation_id']['id'], reservation_holder.get('position'), reservation_holder.get('time'), reservation_holder.get('initial_configuration'), reservation_holder.get('end_data'), reservation_holder.get('url'), reservation_holder.get('finished'), reservation_holder.get('initial_data'), remote_reservation_id)

    @possibleKeyError
    def _parse_user(self, holder):
        return User(holder['login'], holder['full_name'], holder['email'], holder['role'])

    @possibleKeyError
    def _parse_command(self, command_holder):
        command = Command.Command(command_holder['commandstring'])
        return command

class BotJSON(AbstractBotDict):
    def __init__(self, url, url_login):
        super(BotJSON, self).__init__(url, url_login)
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.weblabsessionid = "<unknown>"

    def _call(self, method, **kwargs):
        params = {}
        for key in kwargs:
            parsed_response = simplify_response(kwargs[key])
            params[key] = parsed_response
        whole_request = json.dumps({
                            "method" : method,
                            "params" : params
                        })
        avoid_sessionid = False
        if method == 'login':
            uopen = self.opener.open(self.url_login,data=whole_request)
        elif method in ('send_command', 'send_file', 'poll'):
            if self.remote_url is None:
                uopen = self.opener.open(self.url,data=whole_request)
            else:
                avoid_sessionid = True
                opener = urllib2.build_opener()
                opener.addheaders.append(('Cookie', 'weblabsessionid=%s' % self.remote_reservation_id.id.split(';')[1]))
                uopen = opener.open(self.remote_url + 'json/', data = whole_request)
        else:
            uopen = self.opener.open(self.url,data=whole_request)
        content = uopen.read()
        if not avoid_sessionid:
            cookies = [ c for c in self.cj if c.name == 'weblabsessionid' ]
            if len(cookies) > 0:
                self.weblabsessionid = cookies[0].value
        response = json.loads(content)
        if response.get('is_exception', False):
            raise Exception(response["message"])
        return response['result']

    def dispose(self):
        self.opener = None
        self.cj     = None


def create_bot(name, url, url_login):
    if name == 'JSON':
        return BotJSON(url, url_login)
    raise NotImplementedError("no bot for %s" % name)

