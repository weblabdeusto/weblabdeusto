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

import json
import requests
import datetime

from voodoo.gen import CoordAddress
from voodoo.sessions.session_id import SessionId
from weblab.core.reservations import Reservation
from weblab.data.command import Command, NullCommand
from weblab.data.experiments import ReservationResult, RunningReservationResult, WaitingReservationResult, CancelledReservationResult, FinishedReservationResult, ExperimentUsage, LoadedFileSent, CommandSent, ExperimentId, ForbiddenReservationResult
from weblab.data.dto.experiments import ExperimentCategory, Experiment, ExperimentClient, ExperimentAllowed
from weblab.data.dto.users import User

class WebLabDeustoClient(object):

    LOGIN_SUFFIX = 'login/json/'
    CORE_SUFFIX  = 'json/'

    def __init__(self, baseurl):
        """
        Creates a WebLabDeustoClient.
        :param baseurl: The base URL of the instance to check against. An example would be: https://weblab.deusto.es/weblab/
        This is essentially the URL to which '/json' will be appended to carry out the actual queries.
        :return:
        """
        self.baseurl         = baseurl
        self.weblabsessionid = "(not set)"

    def _call(self, url, method, user_agent, **kwargs):
        request = json.dumps({
            'method' : method,
            'params' : kwargs
        })
        headers = {
            'User-agent' : user_agent or 'WebLab-Deusto',
            'content-type': 'application/json',
        }
        cookies = { 'weblabsessionid' : self.weblabsessionid, 'loginweblabsessionid' : self.weblabsessionid }
        r = requests.post(url, data = request, headers = headers, cookies = cookies)
        weblabsessionid = r.cookies.get('weblabsessionid')
        if weblabsessionid:
            self.weblabsessionid = weblabsessionid
        r.raise_for_status()
        response = r.json()
        if response.get('is_exception', False):
            raise Exception(response["message"])
        return response['result']

    def _login_call(self, method, user_agent = None, **kwargs):
        return self._call(self.baseurl + self.LOGIN_SUFFIX, method, user_agent, **kwargs)

    def _core_call(self, method, user_agent = None, **kwargs):
        return self._call(self.baseurl + self.CORE_SUFFIX, method, user_agent, **kwargs)

    def get_cookies(self):
        return { 'weblabsessionid' : self.weblabsessionid }

    def set_cookies(self, cookies):
        self.weblabsessionid = cookies['weblabsessionid']

    def login(self, username, password):
        session_holder = self._login_call('login', username=username, password=password)
        return SessionId(session_holder['id'])

    def reserve_experiment(self, session_id, experiment_id, client_initial_data, consumer_data, user_agent = None):
        serialized_session_id = {'id' : session_id.id}
        serialized_experiment_id = {
                                'exp_name' : experiment_id.exp_name,
                                'cat_name' : experiment_id.cat_name
                            }
        reservation_holder = self._core_call('reserve_experiment',
                        user_agent = user_agent,
                        session_id=serialized_session_id,
                        experiment_id=serialized_experiment_id,
                        client_initial_data=client_initial_data,
                        consumer_data=consumer_data)
        reservation = self._parse_reservation_holder(reservation_holder)
        return reservation

    def logout(self, session_id):
        serialized_session_id = {'id' : session_id.id}
        return self._core_call('logout', session_id = serialized_session_id)

    def get_user_information(self, session_id):
        serialized_session_id     = {'id' : session_id.id}
        user_information = self._core_call('get_user_information', session_id = serialized_session_id)
        user = User(user_information['login'], user_information['full_name'], user_information['email'], user_information['role']['name'])
        user.remainder = user_information
        return user

    def list_experiments(self, session_id):
        serialized_session_id     = {'id' : session_id.id}
        experiment_list = self._core_call('list_experiments', session_id = serialized_session_id)
        experiments = []
        for external_experiment in experiment_list:
            category = ExperimentCategory(external_experiment['experiment']['category']['name'])
            # 2012-04-10T15:22:38
            start_date = datetime.datetime.strptime(external_experiment['experiment']['start_date'], "%Y-%m-%dT%H:%M:%S")
            end_date   = datetime.datetime.strptime(external_experiment['experiment']['end_date'], "%Y-%m-%dT%H:%M:%S")
            if 'client' in external_experiment['experiment']:
                client = ExperimentClient(external_experiment['experiment']['client'], {})
            else:
                client = None
            if 'permission_id' in external_experiment:
                permission_id = external_experiment['permission_id']
                permission_scope = external_experiment['permission_scope']
            else:
                permission_id = None
                permission_scope = None

            exp = Experiment(name = external_experiment['experiment']['name'], category = category, start_date = start_date, end_date = end_date, client = client)
            exp_allowed = ExperimentAllowed(exp, time_allowed = external_experiment['time_allowed'], priority = external_experiment['priority'], initialization_in_accounting = external_experiment['initialization_in_accounting'], permanent_id = external_experiment['permanent_id'], permission_id = permission_id, permission_scope = permission_scope)
            experiments.append(exp_allowed)
        return experiments

    def get_experiment_use_by_id(self, session_id, reservation_id):
        serialized_session_id     = {'id' : session_id.id}
        serialized_reservation_id = {'id' : reservation_id.id}
        experiment_result = self._core_call('get_experiment_use_by_id', session_id = serialized_session_id, reservation_id = serialized_reservation_id)
        return self._parse_experiment_result(experiment_result)

    def get_experiment_uses_by_id(self, session_id, reservation_ids):
        serialized_session_id     = {'id' : session_id.id}
        serialized_reservation_ids = []
        for reservation_id in reservation_ids:
            serialized_reservation_id = {'id' : reservation_id.id}
            serialized_reservation_ids.append(serialized_reservation_id)

        serialized_experiment_results = self._core_call('get_experiment_uses_by_id', session_id = serialized_session_id, reservation_ids = serialized_reservation_ids)
        experiment_results = []
        for serialized_experiment_result in serialized_experiment_results:
            experiment_result = self._parse_experiment_result(serialized_experiment_result)
            experiment_results.append(experiment_result)

        return experiment_results

    def send_command(self, reservation_id, command):
        serialized_reservation_id = {'id' : reservation_id.id}
        serialized_command = { 'commandstring' : command.commandstring }
        response_command = self._core_call('send_command', reservation_id = serialized_reservation_id, command = serialized_command)
        return Command(response_command['commandstring'] if 'commandstring' in response_command and response_command['commandstring'] is not None else NullCommand())

    def send_async_command(self, reservation_id, command):
        serialized_reservation_id = {'id' : reservation_id.id}
        serialized_command = { 'commandstring' : command.commandstring }
        request_id = self._core_call('send_async_command', reservation_id = serialized_reservation_id, command = serialized_command)
        return request_id

    def send_file(self, reservation_id, file_content, file_info):
        serialized_reservation_id = {'id' : reservation_id.id}
        response_command = self._core_call('send_file', reservation_id = serialized_reservation_id, file_content = file_content, file_info = file_info)
        return Command(response_command['commandstring'] if 'commandstring' in response_command and response_command['commandstring'] is not None else NullCommand())

    def send_async_file(self, reservation_id, file_content, file_info):
        serialized_reservation_id = {'id' : reservation_id.id}
        request_id = self._core_call('send_async_file', reservation_id = serialized_reservation_id, file_content = file_content, file_info = file_info)
        return request_id

    def check_async_command_status(self, reservation_id, request_identifiers):
        serialized_reservation_id = {'id' : reservation_id.id}
        response = self._core_call('check_async_command_status', reservation_id = serialized_reservation_id, request_identifiers = request_identifiers)
        return response

    def get_reservation_status(self, reservation_id):
        serialized_reservation_id = {'id' : reservation_id.id}
        reservation_holder = self._core_call('get_reservation_status',reservation_id=serialized_reservation_id)
        reservation = self._parse_reservation_holder(reservation_holder)
        return reservation

    def poll(self, reservation_id):
        serialized_reservation_id = {'id' : reservation_id.id}
        response = self._core_call('poll',reservation_id=serialized_reservation_id)
        return response

    def finished_experiment(self, reservation_id):
        serialized_reservation_id = {'id' : reservation_id.id}
        self._core_call('finished_experiment',reservation_id=serialized_reservation_id)

    def _parse_reservation_holder(self, reservation_holder):
        if reservation_holder.get('remote_reservation_id') is None:
            remote_reservation_id = None
        else:
            remote_reservation_id = reservation_holder['remote_reservation_id'].get('id')

        return Reservation.translate_reservation_from_data(reservation_holder['status'], reservation_holder['reservation_id']['id'], reservation_holder.get('position'), reservation_holder.get('time'), reservation_holder.get('initial_configuration'), reservation_holder.get('end_data'), reservation_holder.get('url'), reservation_holder.get('finished'), reservation_holder.get('initial_data'), remote_reservation_id)

    def _parse_experiment_result(self, experiment_result):
        if experiment_result['status'] == ReservationResult.ALIVE:
            if experiment_result['running']:
                return RunningReservationResult()
            else:
                return WaitingReservationResult()
        elif experiment_result['status'] == ReservationResult.CANCELLED:
            return CancelledReservationResult()
        elif experiment_result['status'] == ReservationResult.FORBIDDEN:
            return ForbiddenReservationResult()

        experiment_use = experiment_result['experiment_use']

        experiment_id = ExperimentId(experiment_use['experiment_id']['exp_name'], experiment_use['experiment_id']['cat_name'])

        addr = experiment_use['coord_address']
        if 'machine_id' in addr:
            coord_address = CoordAddress(addr['machine_id'],addr['instance_id'],addr['server_id'])
        else:
            coord_address = CoordAddress(addr['host'],addr['process'],addr['component'])

        use = ExperimentUsage(experiment_use['experiment_use_id'], experiment_use['start_date'], experiment_use['end_date'], experiment_use['from_ip'], experiment_id, experiment_use['reservation_id'], coord_address, experiment_use['request_info'])
        for sent_file in experiment_use['sent_files']:
            response = Command(sent_file['response']['commandstring']) if 'commandstring' in sent_file['response'] and sent_file['response'] is not None else NullCommand
            if sent_file['file_info'] == {}:
                file_info = None
            else:
                file_info = sent_file['file_info']
            unserialized_sent_file = LoadedFileSent( sent_file['file_content'], sent_file['timestamp_before'], response, sent_file['timestamp_after'], file_info)
            use.append_file(unserialized_sent_file)

        for command in experiment_use['commands']:
            request = Command(command['command']['commandstring']) if 'commandstring' in command['command'] and command['command'] is not None else NullCommand
            response_command = command['response']['commandstring'] if 'commandstring' in command['response'] and command['response'] is not None else None
            if response_command is None or response_command == {}:
                response = NullCommand()
            else:
                response = Command(response_command)
            
            if command['timestamp_after'] is None or command['timestamp_after'] == {}:
                timestamp_after = None
            else:
                timestamp_after = command['timestamp_after']
            unserialized_command = CommandSent(request, command['timestamp_before'], response, timestamp_after)
            use.append_command(unserialized_command)
        return FinishedReservationResult(use)

