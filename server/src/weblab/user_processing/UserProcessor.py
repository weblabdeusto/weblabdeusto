#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import time as time_module
import json
import voodoo.hashing as hashing

import weblab.data.ServerType as ServerType
import weblab.data.Command as Command

from voodoo.cache import cache
import voodoo.ResourceManager as ResourceManager
import voodoo.log as log

import weblab.facade.RemoteFacadeContext as RemoteFacadeContext

import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc
import weblab.user_processing.Reservation as Reservation
import weblab.user_processing.coordinator.WebLabSchedulingStatus as WebLabSchedulingStatus
import weblab.exceptions.laboratory.LaboratoryExceptions as LaboratoryExceptions

import weblab.experiment.Util as ExperimentUtil
import weblab.data.experiments.Usage as Usage

_resource_manager = ResourceManager.CancelAndJoinResourceManager("UserProcessor")

#TODO: configuration
LIST_EXPERIMENTS_CACHE_TIME     = 15  # seconds
GET_GROUPS_CACHE_TIME           = 15  # seconds
GET_ROLES_CACHE_TIME            = 15  # seconds
GET_USERS_CACHE_TIME            = 15  # seconds
GET_EXPERIMENTS_CACHE_TIME      = 15  # seconds
GET_EXPERIMENT_USES_CACHE_TIME  = 15  # seconds
GET_USER_INFORMATION_CACHE_TIME = 200 # seconds
GET_USER_PERMISSIONS_CACHE_TIME = 200 # seconds
DEFAULT_EXPERIMENT_POLL_TIME    = 300  # seconds
EXPERIMENT_POLL_TIME            = 'core_experiment_poll_time'

@cache(LIST_EXPERIMENTS_CACHE_TIME, _resource_manager)
def list_experiments(db_manager, db_session_id):
    return db_manager.get_available_experiments(db_session_id)

@cache(GET_USER_INFORMATION_CACHE_TIME, _resource_manager)
def get_user_information(db_manager, db_session_id):
    return db_manager.retrieve_user_information(db_session_id)

@cache(GET_GROUPS_CACHE_TIME, _resource_manager)
def get_groups(db_manager, db_session_id, parent_id):
    return db_manager.get_groups(db_session_id, parent_id)

@cache(GET_ROLES_CACHE_TIME, _resource_manager)
def get_roles(db_manager, db_session_id):
    return db_manager.get_roles(db_session_id)

@cache(GET_USERS_CACHE_TIME, _resource_manager)
def get_users(db_manager, db_session_id):
    """ Retrieves the users from the database, through the database manager. """
    return db_manager.get_users(db_session_id)

@cache(GET_EXPERIMENTS_CACHE_TIME, _resource_manager)
def get_experiments(db_manager, db_session_id):
    return db_manager.get_experiments(db_session_id)

@cache(GET_EXPERIMENT_USES_CACHE_TIME, _resource_manager)
def get_experiment_uses(db_manager, db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
    return db_manager.get_experiment_uses(db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)

@cache(GET_USER_PERMISSIONS_CACHE_TIME, _resource_manager)
def get_user_permissions(db_manager, db_session_id):
    return db_manager.get_user_permissions(db_session_id)


class UserProcessor(object):

    EXPIRATION_TIME_NOT_SET=-1234

    def __init__(self, locator, session, cfg_manager, coordinator, db_manager, commands_store):
        self._locator         = locator
        self._session         = session
        self._cfg_manager     = cfg_manager
        self._coordinator     = coordinator
        self._db_manager      = db_manager
        self._commands_store  = commands_store
        self.time_module      = time_module

    def list_experiments(self):
        db_session_id         = self._session['db_session_id']
        return list_experiments(self._db_manager, db_session_id)

    def get_user_information(self):
        db_session_id               = self._session['db_session_id']
        user_information            = get_user_information(self._db_manager, db_session_id)
        self._session['user_information'] = user_information
        return user_information

    def get_session(self):
        return self._session

    def get_session_id(self):
        return self._session['session_id']

    # 
    # Experiments
    # 

    def reserve_experiment(self, experiment_id, serialized_client_initial_data, client_address):

        context = RemoteFacadeContext.get_context()

        user_information = self.get_user_information()

        self._session['experiment_id'] = experiment_id

        reservation_info = self._session['reservation_information'] = {}
        reservation_info['user_agent']    = context.get_user_agent()
        reservation_info['referer']       = context.get_referer()
        reservation_info['mobile']        = context.is_mobile()
        reservation_info['facebook']      = context.is_facebook()
        reservation_info['from_ip']       = client_address.client_address
        reservation_info['username']      = self._session['db_session_id'].username
        reservation_info['role']          = self._session['db_session_id'].role

        try:
            client_initial_data = json.loads(serialized_client_initial_data)
        except ValueError:
            # TODO: to be tested
            raise UserProcessingExceptions.UserProcessingException(
                    "Invalid client_initial_data provided: a json-serialized object expected"
            )

        experiments = [ 
                exp for exp in self.list_experiments()
                if exp.experiment.name           == experiment_id.exp_name 
                and exp.experiment.category.name == experiment_id.cat_name
            ]

        if len(experiments) == 0:
            raise UserProcessingExceptions.UnknownExperimentIdException(
                    "User can't access that experiment (or that experiment type does not exist)"
            )

        user_information = self.get_user_information()
        experiment_allowed = experiments[0]
        try:
            status, reservation_id    = self._coordinator.reserve_experiment(
                    experiment_allowed.experiment.to_experiment_id(), 
                    experiment_allowed.time_allowed, 
                    experiment_allowed.priority,
                    client_initial_data,
                    reservation_info
                )
        except CoordExc.ExperimentNotFoundException:
            raise UserProcessingExceptions.NoAvailableExperimentFoundException(
                "No experiment of type <%s,%s> is currently deployed" % (
                        experiment_id.exp_name, 
                        experiment_id.cat_name
                    )
            )


        self._session['reservation_information'].pop('from_ip', None)

        self._session['reservation_id']   = reservation_id
            
        self._initialize_polling()

        if status.status == WebLabSchedulingStatus.WebLabSchedulingStatus.RESERVED:
            self._process_reserved_status(status)

        return Reservation.Reservation.translate_reservation(
                    status
                )

    def get_reservation_status(self):
        reservation_id = self._session.get('reservation_id') or self._session.get('last_reservation_id')
        if reservation_id is not None:
            try:
                status = self._coordinator.get_reservation_status(reservation_id)
            except CoordExc.ExpiredSessionException:
                self._session.pop('reservation_id', None)
            else:
                if status.status == WebLabSchedulingStatus.WebLabSchedulingStatus.RESERVED:
                    self._process_reserved_status(status)

                return Reservation.Reservation.translate_reservation(
                        status
                    )
        else:
            pass # TODO

    def _process_reserved_status(self, status):
        if 'lab_session_id' in self._session:
            return

        self._session['lab_session_id'] = status.lab_session_id
        self._session['lab_coordaddr']  = status.coord_address
        self._session['experiment_time_left'] = self.time_module.time() + status.time
        self._renew_expiration_time(
                self.time_module.time() + status.time
            )


    def finished_experiment(self):
        error = None
        if self._session.has_key('reservation_id'):
            try:
                reservation_id = self._session.pop('reservation_id')
                self._session['last_reservation_id'] = reservation_id
                self._coordinator.finish_reservation(reservation_id)
            except Exception, e:
                log.log( UserProcessor, log.LogLevel.Error, "Exception finishing reservation: %s" % e )
                log.log_exc( UserProcessor, log.LogLevel.Warning )
                error = e

        self._stop_polling()
        self._session.pop('lab_session_id', None)

        if error is not None:
            raise UserProcessingExceptions.FailedToFreeReservationException(
                    "There was an error freeing reservation: %s" % error
                )

    def logout(self):
        if self._session.has_key('lab_session_id'): # TODO: improve this
            self.finished_experiment()

    def send_file(self, file_content, file_info ):
        if self._session.has_key('lab_session_id') and self._session.has_key('lab_coordaddr'):
            laboratory_server = self._locator.get_server_from_coordaddr(
                    self._session['lab_coordaddr'],
                    ServerType.Laboratory
                )

            usage_file_sent = self._store_file(file_content, file_info)
            try:
                # TODO XXX FIXME
                # file_sent_id = self._session['experiment_usage'].append_file(usage_file_sent)
                response = laboratory_server.send_file(
                        self._session['lab_session_id'],
                        file_content,
                        file_info
                    )

                # TODO XXX FIXME
                # usage_file_sent.response        = response
                # usage_file_sent.timestamp_after = self._utc_timestamp()
                # self._session['experiment_usage'].update_file(file_sent_id, usage_file_sent)
                return response
            except LaboratoryExceptions.SessionNotFoundInLaboratoryServerException:
                try:
                    self.finished_experiment()
                except UserProcessingExceptions.FailedToFreeReservationException:
                    pass
                raise UserProcessingExceptions.NoCurrentReservationException(
                    'Experiment reservation expired'
                )
            except LaboratoryExceptions.FailedToSendFileException, ftspe:
                try:
                    self.finished_experiment()
                except UserProcessingExceptions.FailedToFreeReservationException:
                    pass
                raise UserProcessingExceptions.FailedToSendFileException(
                        "Failed to send file: %s" % ftspe
                    )
        else:
            pass # TODO

    def send_command(self, command):
        if self._session.has_key('lab_session_id') and self._session.has_key('lab_coordaddr'):
            laboratory_server = self._locator.get_server_from_coordaddr(
                    self._session['lab_coordaddr'],
                    ServerType.Laboratory
                )
            command_id_pack = self._append_command(command)
            try:
                response = laboratory_server.send_command(
                        self._session['lab_session_id'],
                        command
                    )

                self._update_command(command_id_pack, response)

                return response
            except LaboratoryExceptions.SessionNotFoundInLaboratoryServerException:
                self._update_command(command_id_pack, Command.Command("ERROR: SessionNotFound: None"))
                try:
                    self.finished_experiment()
                except UserProcessingExceptions.FailedToFreeReservationException:
                    pass
                raise UserProcessingExceptions.NoCurrentReservationException(
                    'Experiment reservation expired'
                )
            except LaboratoryExceptions.FailedToSendCommandException, ftspe:
                self._update_command(command_id_pack, Command.Command("ERROR: " + str(ftspe)))
                try:
                    self.finished_experiment()
                except UserProcessingExceptions.FailedToFreeReservationException:
                    pass

                raise UserProcessingExceptions.FailedToSendCommandException(
                        "Failed to send command: %s" % ftspe
                    )
        else:
            pass # TODO

    def update_latest_timestamp(self):
        self._session['latest_timestamp'] = self._utc_timestamp()

    def _append_command(self, command):
        # TODO XXX FIXME
        return None, None
        timestamp_before = self._utc_timestamp()
        command_sent = Usage.CommandSent(command, timestamp_before)
        return self._session['experiment_usage'].append_command(command_sent), command_sent

    def _update_command(self, (command_id, command_sent), response):
        # TODO XXX FIXME
        return
        timestamp_after = self._utc_timestamp()
        command_sent.response        = response
        command_sent.timestamp_after = timestamp_after
        self._session['experiment_usage'].update_command(command_id, command_sent)

    def _utc_timestamp(self):
        return self.time_module.time()

    def _store_file(self, file_content, file_info):
        # TODO: this is a very dirty way to implement this. Anyway until the good approach is taken, this will store the students programs
        # TODO: there should be two global variables: first, if store_student_files is not activated, do nothing.
        #       but, if store_student_files is activated, it should check that for a given experiment, they should be stored or not.
        #       For instance, I may want to store GPIB experiments but not FPGA experiments
        should_i_store = self._cfg_manager.get_value('core_store_students_programs',False)
        timestamp_before   = self._utc_timestamp()
        if should_i_store:
            # TODO not tested
            def get_time_in_str():
                cur_time = time_module.time()
                s = time_module.strftime('%Y_%m_%d___%H_%M_%S_',time_module.gmtime(cur_time))
                millis = int((cur_time - int(cur_time)) * 1000)
                return s + str(millis)

            if isinstance(file_content, unicode):
                file_content_encoded = file_content.encode('utf8')
            else:
                file_content_encoded = file_content
            deserialized_file_content = ExperimentUtil.deserialize(file_content_encoded)
            storage_path = self._cfg_manager.get_value('core_store_students_programs_path')
            user_information = self.get_user_information()
            relative_file_path = get_time_in_str() + '_' + user_information.login + '_' + self._session['session_id'].id
            sha_obj            = hashing.new('sha')
            sha_obj.update(deserialized_file_content)
            file_hash          = sha_obj.hexdigest()

            where = storage_path + '/' + relative_file_path
            f = open(where,'w')
            f.write(deserialized_file_content)
            f.close()

            return Usage.FileSent(relative_file_path, "{sha}%s" % file_hash, timestamp_before, file_info = file_info)
        else:
            return Usage.FileSent("<file not stored>","<file not stored>", timestamp_before, file_info = file_info)

    #
    # Polling
    # 

    def _initialize_polling(self):
        self._session['session_polling'] = (
                self.time_module.time(),
                UserProcessor.EXPIRATION_TIME_NOT_SET
            )

    def poll(self):
        if self.is_polling():
            latest_poll, expiration_time = self._session['session_polling']
            self._session['session_polling'] = (
                    self.time_module.time(),
                    UserProcessor.EXPIRATION_TIME_NOT_SET
                )

    def _stop_polling(self):
        if self.is_polling():
            self._session.pop('session_polling')

    def _renew_expiration_time(self, expiration_time):
        if self.is_polling():
            self._session['session_polling'] = (
                    self.time_module.time(),
                    expiration_time
                )

    def is_expired(self):
        if not self.is_polling():
            return True

        current_time = self.time_module.time()
        latest_poll, expiration_time = self._session['session_polling']
        if current_time - latest_poll > self._cfg_manager.get_value(EXPERIMENT_POLL_TIME, DEFAULT_EXPERIMENT_POLL_TIME):
            return True
        elif expiration_time != UserProcessor.EXPIRATION_TIME_NOT_SET and current_time > expiration_time:
            return True
        return False

    def is_polling(self):
        return self._session.has_key('session_polling')
    
    #
    # admin service
    #
    
    def get_users(self):
        db_session_id        = self._session['db_session_id']
        return get_users(self._db_manager, db_session_id)

    def get_groups(self, parent_id=None):
        db_session_id         = self._session['db_session_id']
        return get_groups(self._db_manager, db_session_id, parent_id)
    
    def get_roles(self):
        db_session_id         = self._session['db_session_id']
        return get_roles(self._db_manager, db_session_id)

    def get_experiments(self):
        db_session_id         = self._session['db_session_id']
        return get_experiments(self._db_manager, db_session_id)

    def get_experiment_uses(self, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
        db_session_id         = self._session['db_session_id']
        return get_experiment_uses(self._db_manager, db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)

    def get_user_permissions(self):
        db_session_id         = self._session['db_session_id']
        return get_user_permissions(self._db_manager, db_session_id)

