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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import threading

from voodoo.log import logged
import voodoo.LogLevel as LogLevel
import voodoo.log as log
import voodoo.counter as counter

import weblab.data.ServerType as ServerType

import weblab.user_processing.UserProcessor as UserProcessor
import weblab.user_processing.AliveUsersCollection as AliveUsersCollection
import weblab.user_processing.coordinator.Coordinator as Coordinator
import weblab.user_processing.coordinator.CoordinationConfigurationParser as CoordinationConfigurationParser
import weblab.user_processing.database.DatabaseManager as DatabaseManager

import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions
import weblab.user_processing.facade.UserProcessingFacadeServer as UserProcessingFacadeServer
import weblab.user_processing.facade.AdminFacadeServer as AdminFacadeServer

from voodoo.gen.caller_checker import caller_check
from voodoo.threaded import threaded

from voodoo.sessions.SessionChecker import check_session
import voodoo.sessions.SessionManager as SessionManager
import voodoo.sessions.SessionType as SessionType

import voodoo.ResourceManager as ResourceManager

check_session_params = (
        UserProcessingExceptions.SessionNotFoundException,
        "User Processing Server"
    )

_resource_manager = ResourceManager.CancelAndJoinResourceManager("UserProcessingServer")

LIST_EXPERIMENTS_CACHE_TIME     = 15 #seconds
GET_USER_INFORMATION_CACHE_TIME = 15 #seconds

CHECKING_TIME_NAME    = 'core_checking_time'
DEFAULT_CHECKING_TIME = 3 # seconds

WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE         = "core_session_type"
DEFAULT_WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE = SessionType.Memory.name
WEBLAB_USER_PROCESSING_SERVER_SESSION_POOL_ID      = "core_session_pool_id"

WEBLAB_USER_PROCESSING_SERVER_CLEAN_COORDINATOR    = "core_coordinator_clean"

class UserProcessingServer(object):

    FACADE_SERVERS = (
                        UserProcessingFacadeServer.UserProcessingRemoteFacadeServer,
                        AdminFacadeServer.AdminRemoteFacadeServer
                    )

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UserProcessingServer,self).__init__(*args, **kwargs)

        session_type    = cfg_manager.get_value(WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE, DEFAULT_WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE) 
        session_pool_id = cfg_manager.get_value(WEBLAB_USER_PROCESSING_SERVER_SESSION_POOL_ID, "UserProcessingServer")
        if session_type in [ stype.name for stype in SessionType.getSessionTypeValues() ]:
            real_session_type = getattr(SessionType, session_type)
            self._session_manager = SessionManager.SessionManager(
                    cfg_manager, real_session_type, session_pool_id
                )
        else:
            raise UserProcessingExceptions.NotASessionTypeException(
                    'Not a session type: %s' % session_type 
                )

        self._cfg_manager    = cfg_manager  
        self._locator        = locator

        self._coordinator    = Coordinator.Coordinator(self._locator, cfg_manager) 

        self._server_route   = cfg_manager.get_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_SERVER_ROUTE, 
                                            UserProcessingFacadeServer.DEFAULT_USER_PROCESSING_SERVER_ROUTE)

        clean = cfg_manager.get_value(WEBLAB_USER_PROCESSING_SERVER_CLEAN_COORDINATOR, True)
        if clean:
            self._coordinator._clean()

        self._db_manager     = DatabaseManager.UserProcessingDatabaseManager(cfg_manager)

        self._alive_users_collection = AliveUsersCollection.AliveUsersCollection(
                self._locator, self._cfg_manager, real_session_type, self._session_manager, self._db_manager)

        if clean:
            self._parse_coordination_configuration()

        self._facade_servers = []
        for FacadeClass in self.FACADE_SERVERS:
            facade_server = FacadeClass(self, cfg_manager)
            self._facade_servers.append(facade_server)
            facade_server.start()

        self._initialize_checker_timer()



    def stop(self):
        if hasattr(super(UserProcessingServer, self), 'stop'):
            super(UserProcessingServer, self).stop()
        for facade_server in self._facade_servers:
            facade_server.stop()

    def _parse_coordination_configuration(self):
        coordination_configuration_parser = CoordinationConfigurationParser.CoordinationConfigurationParser(self._cfg_manager)
        configuration = coordination_configuration_parser.parse_configuration()
        for laboratory_server_coord_address_str in configuration:
            experiment_instance_config = configuration[laboratory_server_coord_address_str]
            for experiment_instance_id in experiment_instance_config:
                resource = experiment_instance_config[experiment_instance_id]
                self._coordinator.add_experiment_instance_id(laboratory_server_coord_address_str, experiment_instance_id, resource)

    def _load_user(self, session):
        return UserProcessor.UserProcessor(self._locator, session, self._cfg_manager, self._coordinator, self._db_manager)

    def _check_user_not_expired_and_poll(self, user_processor):
        if user_processor.is_expired():
            user_processor.finished_experiment()
            raise UserProcessingExceptions.NoCurrentReservationException(
                'Current user does not have any experiment assigned'
            )
        else:
            user_processor.poll()
            user_processor.update_latest_timestamp()
            # It's already locked, we just update that this user is still among us
            self._session_manager.modify_session(
                    user_processor.get_session_id(),
                    user_processor.get_session()
                )
    
    def _check_other_sessions_finished(self):
        expired_users = self._alive_users_collection.check_expired_users()
        if len(expired_users) > 0:
            self._expire_users(expired_users)

    @threaded(_resource_manager)
    def _expire_users(self, expired_users):
        for expired_user in expired_users:
            try:
                expired_session = self._session_manager.get_session_locking(expired_user)
                try:
                    user            = self._load_user(expired_session)
                    if user.is_expired():
                        user.finished_experiment()
                finally:
                    self._session_manager.modify_session_unlocking(expired_user, expired_session)
            except Exception, e:
                log.log(
                    UserProcessingServer,
                    LogLevel.Warning,
                    "Exception freeing experiment of %s: %s" % (expired_user, e)
                )
                log.log_exc(
                    UserProcessingServer,
                    LogLevel.Info
                )

    def _initialize_checker_timer(self):
        checking_time = self._cfg_manager.get_value(CHECKING_TIME_NAME, DEFAULT_CHECKING_TIME)
        timer = threading.Timer(checking_time, self._renew_checker_timer)
        timer.setName(counter.next_name("ups-checker-timer"))
        timer.setDaemon(True)
        timer.start()
        _resource_manager.add_resource(timer)

    def _renew_checker_timer(self):
        self._check_other_sessions_finished()
        self._initialize_checker_timer()

    # # # # # # # # # # # #
    # Session operations  #
    # # # # # # # # # # # #

    @caller_check(ServerType.Login)
    @logged(LogLevel.Info)
    def do_reserve_session(self, db_session_id):
        session_id = self._session_manager.create_session()
        initial_session = {
            'db_session_id'       : db_session_id,
            'session_id'          : session_id,
            'latest_timestamp'      : 0 # epoch
        }
        user_processor = self._load_user(initial_session)
        user_processor.get_user_information()
        user_processor.update_latest_timestamp()
        self._session_manager.modify_session(session_id,initial_session)
        return session_id, self._server_route

    @logged(LogLevel.Info)
    def logout(self, session_id):
        if self._session_manager.has_session(session_id):
            session        = self._session_manager.get_session(session_id)

            self._alive_users_collection.remove_user(session_id)
            user_processor = self._load_user(session)
            user_processor.logout()
            user_processor.update_latest_timestamp()

            self._session_manager.delete_session(session_id)
        else:
            raise UserProcessingExceptions.SessionNotFoundException(
                "User Processing Server session not found"
            )

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def list_experiments(self,session):
        user_processor = self._load_user(session)
        try:
            return user_processor.list_experiments()
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_user_information(self, session):
        user_processor = self._load_user(session)
        try:
            return user_processor.get_user_information()
        finally:
            user_processor.update_latest_timestamp()

    # # # # # # # # # # # # # # # # #
    # Experiment related operations #
    # # # # # # # # # # # # # # # # #

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def reserve_experiment(self, session, experiment_id, client_address):
        user_processor = self._load_user(session)
        try:
            self._alive_users_collection.add_user(session['session_id'])
            return user_processor.reserve_experiment( experiment_id, client_address ) 
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def finished_experiment(self, session):
        user_processor = self._load_user(session)
        try:
            self._alive_users_collection.remove_user(session['session_id'])
            return user_processor.finished_experiment()
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info, except_for=(('file_content',2),))
    @check_session(*check_session_params)
    def send_file(self, session, file_content, file_info):
        """ send_file(session_id, file_content, file_info)

        Sends file to the experiment.
        """
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
            return user_processor.send_file( file_content, file_info )
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def send_command(self, session, command):
        """ send_command(session_id, command)

        send_command sends an abstract string <command> which will be unpacked by the
        experiment.
        """
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
            return user_processor.send_command( command )
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def poll(self, session):
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
        except UserProcessingExceptions.NoCurrentReservationException:
            pass

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_reservation_status(self, session):
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
            return user_processor.get_reservation_status()
        finally:
            user_processor.update_latest_timestamp()

    #
    # admin service
    #

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_groups(self, session, parent_id=None):
        user_processor = self._load_user(session)
        try:
            return user_processor.get_groups(parent_id)
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_experiments(self, session):
        user_processor = self._load_user(session)
        try:
            return user_processor.get_experiments()
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_experiment_uses(self, session, from_date=None, to_date=None, group_id=None, experiment_id=None, start_row=None, end_row=None, sort_by=None):
        user_processor = self._load_user(session)
        try:
            return user_processor.get_experiment_uses(from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)
        finally:
            user_processor.update_latest_timestamp()
            
    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_roles(self, session):
        user_processor = self._load_user(session)
        try:
            return user_processor.get_roles()
        finally:
            user_processor.update_latest_timestamp()
            
    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_users(self, session):
        """
        Receives the get_users petition sent by the client and handles the request through
        a user processor for the calling session.
        """
        user_processor = self._load_user(session)
        try:
            return user_processor.get_users()
        finally:
            user_processor.update_latest_timestamp()

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    def get_user_permissions(self, session):
        user_processor = self._load_user(session)
        try:
            return user_processor.get_user_permissions()
        finally:
            user_processor.update_latest_timestamp()

