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

import time
import threading

from voodoo.log import logged
import voodoo.log as log
import voodoo.counter as counter

import weblab.data.server_type as ServerType

import weblab.core.data_retriever as TemporalInformationRetriever
import weblab.core.processor as UserProcessor
import weblab.core.alive_users as AliveUsersCollection
import weblab.core.coordinator.coordinator as Coordinator
import weblab.core.coordinator.config_parser as CoordinationConfigurationParser
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.db.manager as DatabaseManager

import weblab.core.exc as coreExc
import weblab.core.comm.user_server as UserProcessingFacadeServer
import weblab.core.comm.admin_server as AdminFacadeServer
import weblab.core.comm.web_server as WebFacadeServer

from voodoo.gen.caller_checker import caller_check
from voodoo.threaded import threaded

from voodoo.sessions.checker import check_session
import voodoo.sessions.manager as SessionManager
import voodoo.sessions.session_type as SessionType

import voodoo.resources_manager as ResourceManager

check_session_params = (
        coreExc.SessionNotFoundException,
        "User Processing Server"
    )

_resource_manager = ResourceManager.CancelAndJoinResourceManager("UserProcessingServer")

LIST_EXPERIMENTS_CACHE_TIME     = 15 #seconds
GET_USER_INFORMATION_CACHE_TIME = 15 #seconds

CHECKING_TIME_NAME    = 'core_checking_time'
DEFAULT_CHECKING_TIME = 3 # seconds

WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE         = "core_session_type"
DEFAULT_WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE = SessionType.Memory
WEBLAB_USER_PROCESSING_SERVER_SESSION_POOL_ID      = "core_session_pool_id"

WEBLAB_USER_PROCESSING_SERVER_CLEAN_COORDINATOR    = "core_coordinator_clean"

def load_user_processor(func):
    def wrapped(self, session, *args, **kwargs):
        user_processor = self._load_user(session)
        try:
            return func(self, user_processor, session, *args, **kwargs)
        finally:
            user_processor.update_latest_timestamp()
    wrapped.__name__ = func.__name__
    wrapped.__doc__  = func.__doc__
    return wrapped

class UserProcessingServer(object):
    """
    The UserProcessingServer will receive client requests, which will be forwarded
    to an appropriate UserProcessor for the specified session identifier.
    """

    FACADE_SERVERS = (
                        UserProcessingFacadeServer.UserProcessingRemoteFacadeServer,
                        AdminFacadeServer.AdminRemoteFacadeServer,
                        WebFacadeServer.UserProcessingWebRemoteFacadeServer
                    )

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UserProcessingServer,self).__init__(*args, **kwargs)

        self._stopping = False 

        session_type    = cfg_manager.get_value(WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE, DEFAULT_WEBLAB_USER_PROCESSING_SERVER_SESSION_TYPE) 
        session_pool_id = cfg_manager.get_value(WEBLAB_USER_PROCESSING_SERVER_SESSION_POOL_ID, "UserProcessingServer")
        if session_type in SessionType.getSessionTypeValues():
            self._session_manager = SessionManager.SessionManager(
                    cfg_manager, session_type, session_pool_id
                )
        else:
            raise coreExc.NotASessionTypeException(
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


        self._commands_store = TemporalInformationStore.CommandsTemporalInformationStore()

        self._temporal_information_retriever = TemporalInformationRetriever.TemporalInformationRetriever(self._coordinator.initial_store, self._coordinator.finished_store, self._commands_store, self._db_manager)
        self._temporal_information_retriever.start()

        self._alive_users_collection = AliveUsersCollection.AliveUsersCollection(
                self._locator, self._cfg_manager, session_type, self._session_manager, self._db_manager, self._commands_store)

        if clean:
            self._parse_coordination_configuration()

        self._facade_servers = []
        for FacadeClass in self.FACADE_SERVERS:
            facade_server = FacadeClass(self, cfg_manager)
            self._facade_servers.append(facade_server)
            facade_server.start()

        self._initialize_checker_timer()



    def stop(self):
        self._stopping = True

        self._temporal_information_retriever.stop()

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
        return UserProcessor.UserProcessor(self._locator, session, self._cfg_manager, self._coordinator, self._db_manager, self._commands_store)

    def _check_user_not_expired_and_poll(self, user_processor, raise_poll_exc = True):
        if user_processor.is_expired():
            user_processor.finished_experiment()
            raise coreExc.NoCurrentReservationException(
                'Current user does not have any experiment assigned'
            )
        else:
            try:
                user_processor.poll()
            except coreExc.NoCurrentReservationException:
                if raise_poll_exc:
                    raise
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
            if self._stopping:
                return
            try:
                expired_session = self._session_manager.get_session_locking(expired_user)
                try:
                    user            = self._load_user(expired_session)
                    if user.is_expired():
                        user.finished_experiment()
                finally:
                    self._session_manager.modify_session_unlocking(expired_user, expired_session)
            except Exception as e:
                log.log(
                    UserProcessingServer,
                    log.level.Warning,
                    "Exception freeing experiment of %s: %s" % (expired_user, e)
                )
                log.log_exc(
                    UserProcessingServer,
                    log.level.Info
                )

    def _initialize_checker_timer(self):
        checking_time = self._cfg_manager.get_value(CHECKING_TIME_NAME, DEFAULT_CHECKING_TIME)
        timer = threading.Timer(checking_time, self._renew_checker_timer)
        timer.setName(counter.next_name("ups-checker-timer"))
        timer.setDaemon(True)
        timer.start()
        _resource_manager.add_resource(timer)

    def _renew_checker_timer(self):
        checking_time = self._cfg_manager.get_value(CHECKING_TIME_NAME, DEFAULT_CHECKING_TIME)
        while not self._stopping:
            self._check_other_sessions_finished()
            time.sleep(checking_time)

    # # # # # # # # # # # #
    # Session operations  #
    # # # # # # # # # # # #

    @caller_check(ServerType.Login)
    @logged(log.level.Info)
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


    @logged(log.level.Info)
    def logout(self, session_id):
        if self._session_manager.has_session(session_id):
            session        = self._session_manager.get_session(session_id)

            self._alive_users_collection.remove_user(session_id)
            user_processor = self._load_user(session)
            user_processor.logout()
            user_processor.update_latest_timestamp()

            self._session_manager.delete_session(session_id)
        else:
            raise coreExc.SessionNotFoundException(
                "User Processing Server session not found"
            )


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def list_experiments(self, user_processor, session):
        return user_processor.list_experiments()


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_user_information(self, user_processor, session):
        return user_processor.get_user_information()

    # # # # # # # # # # # # # # # # #
    # Experiment related operations #
    # # # # # # # # # # # # # # # # #

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def reserve_experiment(self, user_processor, session, experiment_id, client_initial_data, client_address):
        self._alive_users_collection.add_user(session['session_id'])
        return user_processor.reserve_experiment( experiment_id, client_initial_data, client_address ) 


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def finished_experiment(self, user_processor, session):
        self._alive_users_collection.remove_user(session['session_id'])
        return user_processor.finished_experiment()


    @logged(log.level.Info, except_for=(('file_content',2),))
    @check_session(*check_session_params)
    @load_user_processor
    def send_file(self, user_processor, session, file_content, file_info):
        """ send_file(session_id, file_content, file_info)

        Sends file to the experiment.
        """
        self._check_user_not_expired_and_poll( user_processor )
        return user_processor.send_file( file_content, file_info )


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def send_command(self, user_processor, session, command):
        """ send_command(session_id, command)

        send_command sends an abstract string <command> which will be unpacked by the
        experiment.
        """
        self._check_user_not_expired_and_poll( user_processor )
        return user_processor.send_command( command )
            
    @logged(log.level.Info, except_for=(('file_content',2),))
    @check_session(*check_session_params)
    def send_async_file(self, session, file_content, file_info):
        """ 
        send_async_file(session_id, file_content, file_info)
        Sends a file asynchronously to the experiment. The response
        will not be the real one, but rather, a request_id identifying
        the asynchronous query. 
        @param session Session
        @param file_content Contents of the file.
        @param file_info File information of the file.
        @see check_async_command_status
        """
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
            return user_processor.send_async_file( file_content, file_info )
        finally:
            user_processor.update_latest_timestamp()

    # TODO: This method should now be finished. Will need to be verified, though.
    @logged(log.level.Info)
    @check_session(*check_session_params)
    def check_async_command_status(self, session, request_identifiers):
        """ 
        check_async_command_status(session_id, request_identifiers)
        Checks the status of several asynchronous commands. 
        
        @param session: Session id
        @param request_identifiers: A list of the request identifiers of the
        requests to check. 
        @return: Dictionary by request-id of the tuples: (status, content)
        """
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
            return user_processor.check_async_command_status( request_identifiers )
        finally:
            user_processor.update_latest_timestamp()

    @logged(log.level.Info)
    @check_session(*check_session_params)
    def send_async_command(self, session, command):
        """ 
        send_async_command(session_id, command)

        send_async_command sends an abstract string <command> which will be unpacked by the
        experiment, and run asynchronously on its own thread. Its status may be checked through
        check_async_command_status.
        """
        user_processor = self._load_user(session)
        try:
            self._check_user_not_expired_and_poll( user_processor )
            return user_processor.send_async_command( command )
        finally:
            user_processor.update_latest_timestamp()


    @logged(log.level.Info)
    @check_session(*check_session_params)
    def poll(self, session):
        user_processor = self._load_user(session)
        self._check_user_not_expired_and_poll( user_processor )


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_reservation_status(self, user_processor, session):
        self._check_user_not_expired_and_poll( user_processor, False )
        return user_processor.get_reservation_status()


    #
    # admin service
    #

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_groups(self, user_processor, session, parent_id=None):
        return user_processor.get_groups(parent_id)


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_experiments(self, user_processor, session):
        return user_processor.get_experiments()


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_experiment_uses(self, user_processor, session, from_date=None, to_date=None, group_id=None, experiment_id=None, start_row=None, end_row=None, sort_by=None):
        return user_processor.get_experiment_uses(from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_roles(self, user_processor, session):
        return user_processor.get_roles()


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_users(self, user_processor, session):
        """
        Receives the get_users petition sent by the client and handles the request through
        a user processor for the calling session.
        """
        return user_processor.get_users()


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @load_user_processor
    def get_user_permissions(self, user_processor, session):
        return user_processor.get_user_permissions()

