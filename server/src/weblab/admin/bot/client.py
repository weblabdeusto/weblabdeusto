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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#

import time
import traceback
import urllib2

import json

import cookielib

import xmlrpclib

import libraries
libraries.load()

import voodoo.sessions.session_id as SessionId
import weblab.core.reservations as Reservation
import weblab.data.command as Command
import weblab.comm.server as RemoteFacadeServer
from weblab.data.dto.experiments import Experiment, ExperimentCategory
from weblab.data.dto.users import User

try:
    import weblab.login.comm.generated.weblabdeusto_client as LoginWebLabDeusto_client
    import weblab.core.comm.generated.weblabdeusto_client as UserProcessingWebLabDeusto_client
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

from exc import InvalidUserOrPasswordException
from exc import ListOfExperimentsIsEmptyException

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

    def wrapped(self, *args, **kargs):
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

    wrapped.__name__ = func.__name__
    wrapped.__doc__  = func.__doc__
    return wrapped

def possibleKeyError(func):
    def wrapped(self, *args, **kargs):
        try:
            return func(self, *args, **kargs)
        except KeyError:
            raise Exception("Unexpected response in method %s with args %s and kargs %s" % (func.__name__, str(args), str(kargs)) )

    wrapped.__name__ = func.__name__
    wrapped.__doc__  = func.__doc__
    return wrapped

class AbstractBot(object):
    def __init__(self, url, url_login):
        super(AbstractBot, self).__init__()
        self.session_id = ""
        self.calls = []
        self.begin = 0
        self.end = 0
        self.url = url
        self.url_login = url_login
        self.raise_exceptions = False

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
            raise InvalidUserOrPasswordException("Unable to login with username=%s and password=%s" % (self.username, self.password))

    @logged
    def do_list_experiments(self):
        experiment_list_holders = self._call('list_experiments',session_id=self.session_id)
        experiments = self._parse_experiment_list_holders(experiment_list_holders)
        if len(experiments) > 0:
            return experiments
        else:
            raise ListOfExperimentsIsEmptyException("Received list of experiments is empty")

    @logged
    def do_reserve_experiment(self, experiment_id, client_initial_data):
        reservation_holder = self._call('reserve_experiment',session_id=self.session_id, experiment_id=experiment_id, client_initial_data=client_initial_data)
        reservation = self._parse_reservation_holder(reservation_holder)
        return reservation

    @logged
    def do_get_reservation_status(self):
        reservation_holder = self._call('get_reservation_status',session_id=self.session_id)
        reservation = self._parse_reservation_holder(reservation_holder)
        return reservation

    @logged
    def do_logout(self):
        return self._call('logout',session_id=self.session_id)

    @logged
    def do_finished_experiment(self):
        return self._call('finished_experiment',session_id=self.session_id)

    @logged
    def do_send_file(self, structure, file_info):
        command_holder = self._call('send_file',session_id=self.session_id, file_content=structure, file_info=file_info)
        command = self._parse_command(command_holder)
        return command

    @logged
    def do_send_command(self, command):
        command_holder = self._call('send_command',session_id=self.session_id, command=command)
        command = self._parse_command(command_holder)
        return command

    @logged
    def do_poll(self):
        return self._call('poll',session_id=self.session_id)

    @logged
    def do_get_user_information(self):
        holder = self._call('get_user_information', session_id=self.session_id)
        return self._parse_user(holder)

    @logged
    def do_get_user_permissions(self):
        holder = self._call('get_user_permissions', session_id=self.session_id)
        print holder
        return self._parse_user(holder)

if ZSI_AVAILABLE:
    class BotZSI(AbstractBot):

        def __init__(self, url, url_login):
            super(BotZSI, self).__init__(url, url_login)
            self.login_ws = LoginWebLabDeusto_client.weblabdeustoLocator().getweblabdeusto(url=url_login)
            self.ups_ws   = UserProcessingWebLabDeusto_client.weblabdeustoLocator().getweblabdeusto(url=url)
            self.weblabsessionid = "<unknown>"

        def _call(self, method, **kwargs):
            if kwargs.has_key('session_id') and not kwargs.has_key('session'):
                kwargs['session'] = kwargs.pop('session_id')
            if kwargs.has_key('file_content') and not kwargs.has_key('content'):
                kwargs['content'] = kwargs.pop('file_content')
            try:
                if method == 'login':
                    return_value = getattr(self.login_ws, method)(**kwargs)
                else:
                    return_value = getattr(self.ups_ws,   method)(**kwargs)
            finally:
                if method == 'login':
                    weblabsessionid = self.login_ws.binding.cookies.get('weblabsessionid')
                    self.ups_ws.binding.cookies['weblabsessionid'] = weblabsessionid
                else:
                    weblabsessionid = self.ups_ws.binding.cookies.get('weblabsessionid')
                if weblabsessionid is not None:
                    self.weblabsessionid = weblabsessionid.value or self.weblabsessionid
            return return_value

        def _parse_session_id(self, session_holder):
            return SessionId.SessionId(session_holder.id)

        def _parse_experiment_list_holders(self, experiment_list_holders):
            experiments = []
            for experiment in [ holder.experiment for holder in experiment_list_holders]:
                category = ExperimentCategory(experiment.category.name)
                exp = Experiment(experiment.name, category, experiment.start_date, experiment.end_date)
                experiments.append(exp)
            return experiments

        def _parse_reservation_holder(self, reservation_holder):
            return Reservation.Reservation.translate_reservation_from_data(reservation_holder.status, reservation_holder.position, reservation_holder.time, reservation_holder.initial_configuration, reservation_holder.end_data)

        def _parse_user(self, holder):
            return User(holder.login, holder.full_name, holder.email, holder.role)

        def _parse_command(self, command_holder):
            command = Command.Command(command_holder.commandstring)
            return command

        def dispose(self):
            self.login_ws = None
            self.ups_ws   = None

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
            exp = Experiment(experiment['name'], category, experiment['start_date'], experiment['end_date'])
            experiments.append(exp)
        return experiments

    @possibleKeyError
    def _parse_reservation_holder(self, reservation_holder):
        return Reservation.Reservation.translate_reservation_from_data(reservation_holder['status'], reservation_holder.get('position'), reservation_holder.get('time'), reservation_holder.get('initial_configuration'), reservation_holder.get('end_data'))

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
            parsed_response = RemoteFacadeServer.simplify_response(kwargs[key])
            params[key] = parsed_response
        whole_request = json.dumps({
                            "method" : method,
                            "params" : params
                        })
        if method == 'login':
            uopen = self.opener.open(self.url_login,data=whole_request)
        else:
            uopen = self.opener.open(self.url,data=whole_request)
        content = uopen.read()
        cookies = [ c for c in self.cj if c.name == 'weblabsessionid' ]
        if len(cookies) > 0:
            self.weblabsessionid = cookies[0].value
        response = json.loads(content)
        if response.has_key('is_exception') and response['is_exception']:
            raise Exception(response["message"])
        return response['result']

    def dispose(self):
        self.opener = None
        self.cj     = None

class _CookiesTransport(xmlrpclib.Transport):
    def send_user_agent(self, connection):
        _CookiesTransport.__bases__[0].send_user_agent(self, connection)
        if hasattr(self, '_sessid_cookie'):
            connection.putheader("Cookie",self._sessid_cookie)
        self.__connection = connection

    def _parse_response(self, *args, **kwargs):
        for header, value in self.__connection.headers.items():
            if header.lower() == 'set-cookie':
                real_value = value.split(';')[0]
                self._sessid_cookie = real_value
                self._bot.weblabsessionid = real_value
        return _CookiesTransport.__bases__[0]._parse_response(self, *args, **kwargs)

class BotXMLRPC(AbstractBotDict):
    def __init__(self, url, url_login):
        super(BotXMLRPC, self).__init__(url, url_login)
        self.server       = xmlrpclib.Server(url)
        self.server_login = xmlrpclib.Server(url_login)
        self.transport = self.server._ServerProxy__transport
        self.transport.__class__  = _CookiesTransport
        self.transport._bot = self

        self.transport_login = self.server_login._ServerProxy__transport
        self.transport_login.__class__  = _CookiesTransport
        self.transport_login._bot = self

    def _call(self, method, **kwargs):
        if method == 'login':
            args   = (kwargs['username'], kwargs['password'])
            result = getattr(self.server_login, method)(*args)
            if hasattr(self.transport_login, '_sessid_cookie'):
                self.transport._sessid_cookie = self.transport_login._sessid_cookie
            return result
        elif method in ('list_experiments','get_reservation_status','logout','finished_experiment','poll','get_user_information'):
            args = (kwargs['session_id'],)
        elif method == 'reserve_experiment':
            args = (kwargs['session_id'],kwargs['experiment_id'],kwargs['client_initial_data'])
        elif method == 'send_file':
            args = (kwargs['session_id'],kwargs['file_content'],kwargs['file_info'])
        elif method == 'send_command':
            args = (kwargs['session_id'],kwargs['command'])
        else:
            raise RuntimeError("Unknown method: %s; Couldn't unpack the parameters" % method)
        return getattr(self.server, method)(*args)

    def dispose(self):
        self.server          = None
        self.server_login    = None
        self.transport       = None
        self.transport_login = None

def create_bot(name, url, url_login):
    if name == 'JSON':
        return BotJSON(url, url_login)
    elif name == 'SOAP' or name == 'ZSI':
        if ZSI_AVAILABLE:
            return BotZSI(url, url_login)
        else:
            raise NotImplementedError("Optional library 'ZSI' is not installed, so BotZSI is not available")
    elif name == 'XMLRPC':
        return BotXMLRPC(url, url_login)
    raise NotImplementedError("no bot for %s" % name)

