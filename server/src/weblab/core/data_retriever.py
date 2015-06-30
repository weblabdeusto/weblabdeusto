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

import threading
import time

import voodoo.log as log

from weblab.data.experiments import CommandSent, ExperimentUsage, FileSent
import weblab.core.file_storer as file_storer
import weblab.data.command as Command

class TemporalInformationRetriever(threading.Thread):
    """
    This class retrieves continuously the information of initial and finished experiments.
    """

    PRINT_ERRORS = True

    def __init__(self, cfg_manager, initial_store, finished_store, commands_store, completed_store, db_manager):
        threading.Thread.__init__(self)

        self.cfg_manager          = cfg_manager
        self.keep_running         = True
        self.initial_store        = initial_store
        self.finished_store       = finished_store
        self.commands_store       = commands_store
        self.completed_store      = completed_store
        self.iterations           = 0
        self.db_manager           = db_manager
        self.timeout              = None # Take the default of TemporalInformationStore
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
        if self.keep_running and self.commands_store.empty() and self.completed_store.empty():
            self.iterate_finish()
        if self.keep_running:
            self.iterate_command()
        if self.keep_running:
            self.iterate_completed()

    def iterate_initial(self):
        initial_information = self.initial_store.get(timeout=self.timeout)
        if initial_information is not None:

            initial_timestamp = time.mktime(initial_information.initial_time.timetuple()) + initial_information.initial_time.microsecond / 1e6
            end_timestamp     = time.mktime(initial_information.end_time.timetuple()) + initial_information.end_time.microsecond / 1e6

            request_info  = initial_information.request_info
            from_ip       = request_info.pop('from_ip','<address not found>')

            try:
                username      = request_info.pop('username')
            except:
                log.log( TemporalInformationRetriever, log.level.Critical, "Provided information did not contain some required fields (such as username or role). This usually means that the reservation has previously been expired. Provided request_info: %r; provided data: %r" % (request_info, initial_information), max_size = 10000)
                log.log_exc( TemporalInformationRetriever, log.level.Critical )
                return

            usage = ExperimentUsage()
            usage.start_date     = initial_timestamp
            usage.from_ip        = from_ip
            usage.experiment_id  = initial_information.experiment_id
            usage.reservation_id = initial_information.reservation_id
            usage.coord_address  = initial_information.exp_coordaddr
            usage.request_info   = initial_information.request_info

            command_request = CommandSent(
                    Command.Command("@@@initial::request@@@"), initial_timestamp,
                    Command.Command(str(initial_information.client_initial_data)), end_timestamp)

            command_response = CommandSent(
                    Command.Command("@@@initial::response@@@"), initial_timestamp,
                    Command.Command(str(initial_information.initial_configuration)), end_timestamp)

            usage.append_command(command_request)
            usage.append_command(command_response)

            self.db_manager.store_experiment_usage(username, usage)

    def iterate_completed(self):
        completed_information = self.completed_store.get(timeout=self.timeout)
        if completed_information is not None:
            username, usage, callback = completed_information
            self.db_manager.store_experiment_usage(username, usage)
            callback()


    def iterate_finish(self):
        information = self.finished_store.get(timeout=self.timeout)            
        if information is not None:
            reservation_id, obj, initial_time, end_time = information

            if not self.commands_store.empty() or not self.completed_store.empty():
                # They have higher priority
                self.finished_store.put(reservation_id, obj, initial_time, end_time)
                return

            initial_timestamp = time.mktime(initial_time.timetuple()) + initial_time.microsecond / 1e6
            end_timestamp     = time.mktime(end_time.timetuple()) + end_time.microsecond / 1e6

            command = CommandSent(
                    Command.Command("@@@finish@@@"), initial_timestamp,
                    Command.Command(str(obj)), end_timestamp)

            if not self.db_manager.finish_experiment_usage(reservation_id, initial_timestamp, command):
                # If it could not be added because the experiment id
                # did not exist, put it again in the queue
                self.finished_store.put(reservation_id, obj, initial_time, end_time)
                time.sleep(0.01)

    def iterate_command(self):
        information = self.commands_store.get(timeout=self.timeout)
        if information is not None:
            all_information = [ information ]
            
            # Retrieve all the remaining information to ensure that it it finally empty,
            # with a maximum of 1000 registries per request
            max_registries = 1000
            counter = 0
            while not self.commands_store.empty() and counter < max_registries:
                counter += 1
                information = self.commands_store.get(timeout=0)
                if information is not None:
                    all_information.append(information)

            command_pairs     = []
            command_responses = []
            command_requests  = {}

            file_pairs        = []
            file_responses    = []
            file_requests     = {}

            backup_information           = {}
            backup_information_responses = {}

            # Process
            for information in all_information:
                if information.is_command:
                    if information.is_before:
                        backup_information[information.entry_id] = information
                        command_requests[information.entry_id] = (information.reservation_id, CommandSent( information.payload, information.timestamp))
                    else:
                        backup_information_responses[information.entry_id] = information
                        command_request = command_requests.pop(information.entry_id, None)
                        if command_request is not None:
                            reservation_id, command_sent = command_request
                            complete_command = CommandSent(
                                                    command_sent.command, command_sent.timestamp_before,
                                                    information.payload, information.timestamp)
                            command_pairs.append((reservation_id, information.entry_id, complete_command))
                        else:
                            with self.entry_id2command_id_lock:
                                command_id = self.entry_id2command_id.pop(information.entry_id, None)
                            if command_id is None:
                                self.commands_store.put(information)
                            else:
                                command_responses.append((information.entry_id, command_id, information.payload, information.timestamp))
                else:
                    if information.is_before:
                        backup_information[information.entry_id] = information
                        file_requests[information.entry_id] = (information.reservation_id, information.payload)
                    else:
                        backup_information_responses[information.entry_id] = information
                        file_request = file_requests.pop(information.entry_id, None)
                        if file_request is not None:
                            reservation_id, file_sent = file_request
                            if file_sent.is_loaded():
                                storer = file_storer.FileStorer(self.cfg_manager, reservation_id)
                                stored = storer.store_file(self, file_sent.file_content, file_sent.file_info)
                                file_path = stored.file_path
                                file_hash = stored.file_hash
                            else:
                                file_path = file_sent.file_path
                                file_hash = file_sent.file_hash

                            complete_file = FileSent(file_path, file_hash, file_sent.timestamp_before,
                                                    information.payload, information.timestamp)
                            file_pairs.append((reservation_id, information.entry_id, complete_file))
                        else:
                            with self.entry_id2command_id_lock:
                                command_id = self.entry_id2command_id.pop(information.entry_id, None)
                            if command_id is None:
                                self.commands_store.put(information)
                            else:
                                file_responses.append((information.entry_id, command_id, information.payload, information.timestamp))

            # At this point, we have all the information processed and 
            # ready to be passed to the database in a single commit
            mappings = self.db_manager.store_commands(command_pairs, command_requests, command_responses, file_pairs, file_requests, file_responses)

            elements_to_backup = []
            with self.entry_id2command_id_lock:
                for entry_id in mappings:
                    command_id = mappings[entry_id]
                    if command_id is not None and command_id is not False:
                        self.entry_id2command_id[entry_id] = mappings[entry_id]
                    else:
                        elements_to_backup.append(entry_id)

            for entry_id in elements_to_backup:
                if entry_id in backup_information:
                    self.commands_store.put(backup_information[entry_id])
                if entry_id in backup_information_responses:
                    self.commands_store.put(backup_information_responses[entry_id])

