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

import json
import urllib2
import cookielib

from voodoo.sessions.session_id import SessionId
from weblab.core.reservations import Reservation
from weblab.data.command import Command

class WebLabDeustoClient(object):
    
    LOGIN_SUFFIX = 'login/json/'
    CORE_SUFFIX  = 'json/'

    def __init__(self, baseurl):
        self.baseurl         = baseurl
        self.cj              = cookielib.CookieJar()
        self.opener          = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.weblabsessionid = "(not set)"

    def _call(self, url, method, **kwargs):
        request = json.dumps({
            'method' : method,
            'params' : kwargs
        })
        uopen = self.opener.open(url, data = request) 
        content = uopen.read()
        cookies = [ c for c in self.cj if c.name == 'weblabsessionid' ]
        if len(cookies) > 0:
            self.weblabsessionid = cookies[0].value
        response = json.loads(content)
        if response.has_key('is_exception') and response['is_exception']:
            raise Exception(response["message"])
        return response['result']

    def _login_call(self, method, **kwargs):
        return self._call(self.baseurl + self.LOGIN_SUFFIX, method, **kwargs)

    def _core_call(self, method, **kwargs):
        return self._call(self.baseurl + self.CORE_SUFFIX, method, **kwargs)

    def get_cookies(self):
        return [ cookie for cookie in self.cj if cookie.name in ['weblabsessionid', 'loginweblabsessionid'] ]
        
    def set_cookies(self, cookies):
        for cookie in cookies:
            self.cj.set_cookie(cookie)

    def set_cookie(self, cookie):
        self.cj.set_cookie(cookie)

    def login(self, username, password):
        session_holder = self._login_call('login', username=username, password=password)
        return SessionId(session_holder['id'])

    def reserve_experiment(self, session_id, experiment_id, client_initial_data, consumer_data):
        serialized_session_id = {'id' : session_id.id}
        serialized_experiment_id = {
                                'exp_name' : experiment_id.exp_name,
                                'cat_name' : experiment_id.cat_name
                            }
        reservation_holder = self._core_call('reserve_experiment',
                        session_id=serialized_session_id, 
                        experiment_id=serialized_experiment_id, 
                        client_initial_data=client_initial_data, 
                        consumer_data=consumer_data)
        reservation = self._parse_reservation_holder(reservation_holder)
        return reservation

    def send_command(self, reservation_id, command):
        serialized_reservation_id = {'id' : reservation_id.id}
        serialized_command = { 'commandstring' : command.commandstring }
        response_command = self._core_call('send_command', reservation_id = serialized_reservation_id, command = serialized_command)
        return Command(response_command['commandstring'])

    def get_reservation_status(self, reservation_id):
        serialized_reservation_id = {'id' : reservation_id.id}
        reservation_holder = self._core_call('get_reservation_status',reservation_id=serialized_reservation_id)
        reservation = self._parse_reservation_holder(reservation_holder)
        return reservation

    def finished_experiment(self, reservation_id):
        serialized_reservation_id = {'id' : reservation_id.id}
        self._core_call('finished_experiment',reservation_id=serialized_reservation_id)

    def _parse_reservation_holder(self, reservation_holder):
        return Reservation.translate_reservation_from_data(reservation_holder['status'], reservation_holder['reservation_id']['id'], reservation_holder.get('position'), reservation_holder.get('time'), reservation_holder.get('initial_configuration'), reservation_holder.get('end_data'), reservation_holder.get('url'), reservation_holder.get('finished'), reservation_holder.get('initial_data'))


