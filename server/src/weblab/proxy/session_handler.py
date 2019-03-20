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
#
from __future__ import print_function, unicode_literals

import hashlib
from weblab.data.experiments import CommandSent, FileSent
from weblab.data.command import Command

from voodoo.sha0 import sha0
import weblab.lab.exc as LaboratoryErrors
import weblab.proxy.exc as ProxyErrors
import time
import weblab.experiment.util as ExperimentUtil


EXPERIMENT_POLL_TIME = 'proxy_experiment_poll_time'

DEFAULT_EXPERIMENT_POLL_TIME = 300  # seconds


class ProxySessionHandler(object):

    _time = time

    EXPIRATION_TIME_NOT_SET = -1234

    def __init__(self, session, laboratory, translator, cfg_manager, locator, session_manager):
        super(ProxySessionHandler, self).__init__()
        self._session = session
        self._laboratory = laboratory
        self._translator = translator
        self._cfg_manager = cfg_manager
        self._locator = locator
        self._session_manager = session_manager

    def _utc_timestamp(self):
        return self._time.time()

    def update_latest_timestamp(self):
        self._session['latest_timestamp'] = self._utc_timestamp()

    def _append_command(self, command, timestamp_before, response, timestamp_after):
        command_sent = CommandSent(command, timestamp_before, response, timestamp_after)
        self._session['commands'].append(command_sent)

    def _append_file(self, file_path, file_hash, timestamp_before, response, timestamp_after, file_info):
        file_sent = FileSent(file_path, file_hash, timestamp_before, response, timestamp_after, file_info)
        self._session['files'].append(file_sent)

    def _is_polling(self):
        return 'session_polling' in self._session

    def _stop_polling(self):
        if self._is_polling():
            self._session.pop('session_polling')

    def _renew_expiration_time(self, expiration_time):
        if self._is_polling():
            self._session['session_polling'] = (self._time.time(), expiration_time)

    def _store_file(self, file_content, user_login, session_id):
        # TODO: this is a very dirty way to implement this.
        # Anyway until the good approach is taken, this will store the students programs.
        def get_time_in_str():
            cur_time = self._time.time()
            s = self._time.strftime('%Y_%m_%d___%H_%M_%S_', self._time.gmtime(cur_time))
            millis = int((cur_time - int(cur_time)) * 1000)
            return s + str(millis)

        file_content = file_content.commandstring
        if isinstance(file_content, unicode):
            file_content_encoded = file_content.encode('utf8')
        else:
            file_content_encoded = file_content
        deserialized_file_content = ExperimentUtil.deserialize(file_content_encoded)
        storage_path = self._cfg_manager.get_value('proxy_store_students_programs_path')
        relative_file_path = get_time_in_str() + '_' + user_login + '_' + session_id
        file_hash = sha0(deserialized_file_content)
        where = storage_path + '/' + relative_file_path
        f = open(where,'w')
        f.write(deserialized_file_content)
        f.close()
        return relative_file_path, "{sha}%s" % file_hash

    #===============================================================================
    # API to Core Server
    #===============================================================================

    def enable_access(self):
        self._session['access_enabled'] = True
        self._session['session_polling'] = (self._time.time(), ProxySessionHandler.EXPIRATION_TIME_NOT_SET)
        self._translator.on_start(self._session['trans_session_id'])

    def disable_access(self):
        self._session['access_enabled'] = False

    def is_expired(self):
        if not self._is_polling():
            return "Y <still-polling>"
        current_time = self._time.time()
        latest_poll, expiration_time = self._session['session_polling']
        if current_time - latest_poll > self._cfg_manager.get_value(EXPERIMENT_POLL_TIME, DEFAULT_EXPERIMENT_POLL_TIME):
            return "Y <poll-time-expired>"
        elif expiration_time != ProxySessionHandler.EXPIRATION_TIME_NOT_SET and current_time > expiration_time:
            return "Y <expiration-time-expired>"
        return "N"

    def retrieve_results(self):
        timestamp_before = self._utc_timestamp()
        translation = self._translator.on_finish(self._session['trans_session_id'])
        if translation is not None:
            timestamp_after = self._utc_timestamp()
            self._append_command(Command("on_finish"), timestamp_before, translation, timestamp_after)
        return self._session['commands'], self._session['files']

    #===============================================================================
    # API to Client
    #===============================================================================

    def poll(self):
        if self._is_polling():
            self._session['session_polling'] = (self._time.time(), ProxySessionHandler.EXPIRATION_TIME_NOT_SET)

    def send_command(self, command):
        translated_command = self._translator.before_send_command(self._session['trans_session_id'], command)
        timestamp_before = self._utc_timestamp()
        try:
            lab_response = self._laboratory.send_command(self._session['lab_sess_id'], command)
            timestamp_after = self._utc_timestamp()
            translated_response = self._translator.after_send_command(self._session['trans_session_id'], lab_response)
            if translated_command is not None or translated_response is not None:
                self._append_command(translated_command, timestamp_before, translated_response, timestamp_after)
            return lab_response
        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            self.disable_access()
            raise ProxyErrors.NoCurrentReservationError('Experiment reservation expired')
        except LaboratoryErrors.FailedToSendCommandError as e:
            self.disable_access()
            raise ProxyErrors.FailedToSendCommandError("Failed to send command: %s" % e)

    def send_file(self, file_content, file_info):
        translated_file = self._translator.before_send_file(self._session['trans_session_id'], file_content)
        timestamp_before = self._utc_timestamp()
        try:
            lab_response = self._laboratory.send_file(self._session['lab_sess_id'], file_content, file_info)
            timestamp_after = self._utc_timestamp()
            translated_response = self._translator.after_send_file(self._session['trans_session_id'], lab_response)
            if translated_file is not None or translated_response is not None:
                if translated_file is not None:
                    file_path, file_hash = self._store_file(translated_file, self._session['user_login'], self._session['reservation_id'])
                else:
                    # TODO: Pending to be tested if we decide this to work like this.
                    file_path, file_hash = ("<file not stored>",) * 2
                self._append_file(file_path, file_hash, timestamp_before, translated_response, timestamp_after, file_info)
            return lab_response
        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            self.disable_access()
            raise ProxyErrors.NoCurrentReservationError('Experiment reservation expired')
        except LaboratoryErrors.FailedToSendFileError as e:
            self.disable_access()
            raise ProxyErrors.FailedToSendFileError("Failed to send file: %s" % e)
