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

import threading
import time

import voodoo.log as log

import weblab.db.session as DbSession
from weblab.data.experiments import CommandSent, ExperimentUsage
import weblab.data.command as Command

class TemporalInformationRetriever(threading.Thread):
    """
    This class retrieves continuously the information of initial and finished experiments.
    """

    PRINT_ERRORS = True

    def __init__(self, initial_store, finished_store, commands_store, db_manager):
        threading.Thread.__init__(self)

        self.keep_running = True
        self.initial_store  = initial_store
        self.finished_store = finished_store
        self.commands_store = commands_store
        self.iterations     = 0
        self.db_manager     = db_manager
        self.timeout        = None
        self.entry_id2command_id  = {}
        self.entry_id2command_id_lock = threading.Lock()
        self.setDaemon(True)

    def run(self):
        while self.keep_running:
            try:
                self.iterations += 1
                self.iterate()
            except:
                if self.PRINT_ERRORS:
                    import traceback
                    traceback.print_exc()
                log.log( TemporalInformationRetriever, log.level.Critical, "Exception iterating in TemporalInformationRetriever!!!")
                log.log_exc( TemporalInformationRetriever, log.level.Critical )

    def stop(self):
        self.keep_running = False

    def iterate(self):
        self.iterate_initial()
        if self.keep_running:
            self.iterate_finish()
        if self.keep_running:
            self.iterate_command()

    def iterate_initial(self):
        initial_information = self.initial_store.get(timeout=self.timeout)
        if initial_information is not None:

            initial_timestamp = time.mktime(initial_information.initial_time.timetuple())
            end_timestamp     = time.mktime(initial_information.end_time.timetuple())

            request_info  = initial_information.request_info
            from_ip       = request_info.pop('from_ip','<address not found>')
            username      = request_info.pop('username')
            role          = request_info.pop('role')

            usage = ExperimentUsage()
            usage.start_date     = initial_timestamp
            usage.from_ip        = from_ip
            usage.experiment_id  = initial_information.experiment_id
            usage.reservation_id = initial_information.reservation_id
            usage.coord_address  = initial_information.exp_coordaddr

            command_request = CommandSent(
                    Command.Command("@@@initial::request@@@"), initial_timestamp,
                    Command.Command(str(initial_information.client_initial_data)), end_timestamp
            )

            command_response = CommandSent(
                    Command.Command("@@@initial::response@@@"), initial_timestamp,
                    Command.Command(str(initial_information.initial_configuration)), end_timestamp
            )

            usage.append_command(command_request)
            usage.append_command(command_response)

            self.db_manager.store_experiment_usage(DbSession.ValidDatabaseSessionId(username, role), initial_information.request_info, usage)

    def iterate_finish(self):
        information = self.finished_store.get(timeout=self.timeout)
        if information is not None:
            reservation_id, obj, initial_time, end_time = information

            initial_timestamp = time.mktime(initial_time.timetuple())
            end_timestamp     = time.mktime(end_time.timetuple())

            command = CommandSent(
                    Command.Command("@@@finish@@@"), initial_timestamp,
                    Command.Command(str(obj)), end_timestamp
            )

            if not self.db_manager.finish_experiment_usage(reservation_id, initial_timestamp, command):
                # If it could not be added because the experiment id
                # did not exist, put it again in the queue
                self.finished_store.put(reservation_id, obj, initial_time, end_time)
                time.sleep(0.01)

    def iterate_command(self):
        information = self.commands_store.get(timeout=self.timeout)
        if information is not None:
            if information.is_command:
                if information.is_before:
                    result = self._process_pre_command(information)
                else: 
                    result = self._process_post_command(information)
            else: # not is_command: is file
                if information.is_before:
                    result = self._process_pre_file(information)
                else: # not is_before
                    result = self._process_post_file(information)
            if result is False:
                self.commands_store.put(information)
                    
    def _process_pre_command(self, information):
        command = CommandSent(
                        information.payload,
                        information.timestamp
                    )

        command_id = self.db_manager.append_command(information.reservation_id, command)
        if command_id is False or command_id is None:
            return False

        with self.entry_id2command_id_lock:
            self.entry_id2command_id[information.entry_id] = command_id

        return True

    def _process_post_command(self, information):

        with self.entry_id2command_id_lock:
            command_id = self.entry_id2command_id.pop(information.entry_id, None)

        if command_id is None: # Command not yet stored
            return False

        response_command = information.payload

        self.db_manager.update_command(command_id, response_command, information.timestamp)

        return True

    def _process_pre_file(self, information):
        file_sent = information.payload 
        command_id = self.db_manager.append_file(information.reservation_id, file_sent)

        if command_id is False or command_id is None:
            return False

        with self.entry_id2command_id_lock:
            self.entry_id2command_id[information.entry_id] = command_id

        return True

    def _process_post_file(self, information):

        with self.entry_id2command_id_lock:
            command_id = self.entry_id2command_id.pop(information.entry_id, None)

        if command_id is None: # Command not yet stored
            return False

        response_command = information.payload

        self.db_manager.update_file(command_id, response_command, information.timestamp)

        return True


