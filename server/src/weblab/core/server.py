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

import sys
import uuid
import time
import threading

from functools import wraps

from voodoo.log import logged
import voodoo.log as log
import voodoo.counter as counter
from voodoo.sessions.session_id import SessionId

import weblab.data.server_type as ServerType

from weblab.comm.context import get_context

import weblab.core.reservations as Reservation
import weblab.core.data_retriever as TemporalInformationRetriever
import weblab.core.user_processor as UserProcessor
from weblab.core.reservation_processor import ReservationProcessor
import weblab.core.alive_users as AliveUsersCollection
import weblab.core.coordinator.coordinator as Coordinator
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.db.manager as DatabaseManager
import weblab.core.coordinator.status as WebLabSchedulingStatus

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

check_session_params = dict(
        exception_to_raise = coreExc.SessionNotFoundException,
        what_session       = "Core Users ",
        cut_session_id     = ';'
    )

check_reservation_session_params = dict(
        exception_to_raise         = coreExc.SessionNotFoundException,
        what_session               = "Core Reservations ",
        session_manager_field_name = "_reservations_session_manager",
        cut_session_id             = ';'
    )

_resource_manager = ResourceManager.CancelAndJoinResourceManager("UserProcessingServer")

LIST_EXPERIMENTS_CACHE_TIME     = 15 #seconds
GET_USER_INFORMATION_CACHE_TIME = 15 #seconds

CHECKING_TIME_NAME    = 'core_checking_time'
DEFAULT_CHECKING_TIME = 3 # seconds

WEBLAB_CORE_SERVER_SESSION_TYPE                 = "core_session_type"
DEFAULT_WEBLAB_CORE_SERVER_SESSION_TYPE         = SessionType.Memory
WEBLAB_CORE_SERVER_SESSION_POOL_ID              = "core_session_pool_id"
WEBLAB_CORE_SERVER_RESERVATIONS_SESSION_POOL_ID = "core_session_pool_id"

WEBLAB_CORE_SERVER_CLEAN_COORDINATOR            = "core_coordinator_clean"

WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER               = "core_universal_identifier"
DEFAULT_WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER       = "00000000-0000-0000-0000-000000000000"
WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN         = "core_universal_identifier_human"
DEFAULT_WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN = "WARNING; MISCONFIGURED SERVER. ADD %s AND %s PROPERTIES" % (WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER, WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN)

def load_user_processor(func):
    @wraps(func)
    def wrapper(self, session, *args, **kwargs):
        user_processor = self._load_user(session)
        try:
            return func(self, user_processor, session, *args, **kwargs)
        finally:
            user_processor.update_latest_timestamp()

    return wrapper

def load_reservation_processor(func):
    @wraps(func)
    def wrapper(self, session, *args, **kwargs):
        reservation_processor = self._load_reservation(session)
        try:
            return func(self, reservation_processor, session, *args, **kwargs)
        finally:
            reservation_processor.update_latest_timestamp()
    return wrapper

def update_session_id(func):
    @wraps(func)
    def wrapper(self, session_id, *args, **kwargs):
        ctx = get_context()
        if ctx is not None and hasattr(session_id, 'id'):
            ctx.session_id = session_id.id
        return func(self, session_id, *args, **kwargs)
    return wrapper

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
        self._cfg_manager    = cfg_manager
        self._locator        = locator

        if cfg_manager.get_value(WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER, 'default') == 'default' or cfg_manager.get_value(WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN, 'default') == 'default':
            generated = uuid.uuid1()
            msg = "Property %(property)s or %(property_human)s not configured. Please establish: %(property)s = '%(uuid)s' and %(property_human)s = 'server at university X'. Otherwise, when federating the experiment it could enter in an endless loop." % {
                'property'       : WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER,
                'property_human' : WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN,
                'uuid'           : generated
            }
            print msg
            print >> sys.stderr, msg
            log.log( UserProcessingServer, log.level.Error, msg)

        self.core_server_universal_id       = cfg_manager.get_value(WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER, DEFAULT_WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER)
        self.core_server_universal_id_human = cfg_manager.get_value(WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN, DEFAULT_WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER_HUMAN)

        #
        # Create session managers
        #

        session_type    = cfg_manager.get_value(WEBLAB_CORE_SERVER_SESSION_TYPE, DEFAULT_WEBLAB_CORE_SERVER_SESSION_TYPE)
        if not session_type in SessionType.getSessionTypeValues():
            raise coreExc.NotASessionTypeException( 'Not a session type: %s' % session_type )

        session_pool_id = cfg_manager.get_value(WEBLAB_CORE_SERVER_SESSION_POOL_ID, "UserProcessingServer")
        self._session_manager              = SessionManager.SessionManager( cfg_manager, session_type, session_pool_id )

        reservations_session_pool_id = cfg_manager.get_value(WEBLAB_CORE_SERVER_RESERVATIONS_SESSION_POOL_ID, "CoreServerReservations")
        self._reservations_session_manager = SessionManager.SessionManager( cfg_manager, session_type, reservations_session_pool_id )

        #
        # Coordination
        #

        self._coordinator    = Coordinator.Coordinator(self._locator, cfg_manager)

        #
        # Database and information storage managers
        #

        self._db_manager     = DatabaseManager.UserProcessingDatabaseManager(cfg_manager)

        self._commands_store = TemporalInformationStore.CommandsTemporalInformationStore()

        self._temporal_information_retriever = TemporalInformationRetriever.TemporalInformationRetriever(self._coordinator.initial_store, self._coordinator.finished_store, self._commands_store, self._db_manager)
        self._temporal_information_retriever.start()

        #
        # Alive users
        #

        self._alive_users_collection = AliveUsersCollection.AliveUsersCollection(
                self._locator, self._cfg_manager, session_type, self._reservations_session_manager, self._coordinator, self._commands_store, self._coordinator.finished_reservations_store)


        #
        # Initialize facade (comm) servers
        #

        self._server_route   = cfg_manager.get_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_SERVER_ROUTE, UserProcessingFacadeServer.DEFAULT_USER_PROCESSING_SERVER_ROUTE)

        self._facade_servers = []
        for FacadeClass in self.FACADE_SERVERS:
            facade_server = FacadeClass(self, cfg_manager)
            self._facade_servers.append(facade_server)
            facade_server.start()

        #
        # Start checking times
        #
        self._initialize_checker_timer()



    def stop(self):
        """ Stops all the servers and threads """
        self._stopping = True

        self._temporal_information_retriever.stop()
        self._coordinator.stop()

        if hasattr(super(UserProcessingServer, self), 'stop'):
            super(UserProcessingServer, self).stop()
        for facade_server in self._facade_servers:
            facade_server.stop()

    def _load_user(self, session):
        return UserProcessor.UserProcessor(self._locator, session, self._cfg_manager, self._coordinator, self._db_manager, self._commands_store)

    def _load_reservation(self, session):
        reservation_id = session['reservation_id']
        return ReservationProcessor(self._cfg_manager, reservation_id, session, self._coordinator, self._locator, self._commands_store)

    def _check_reservation_not_expired_and_poll(self, reservation_processor, check_expired = True):
        if check_expired and reservation_processor.is_expired():
            reservation_processor.finish()
            raise coreExc.NoCurrentReservationException( 'Current user does not have any experiment assigned' )

        try:
            reservation_processor.poll()
        except coreExc.NoCurrentReservationException:
            if check_expired:
                raise
        reservation_processor.update_latest_timestamp()
        # It's already locked, we just update that this user is still among us
        self._reservations_session_manager.modify_session(
                reservation_processor.get_reservation_session_id(),
                reservation_processor.get_session()
            )

    def _check_other_sessions_finished(self):
        expired_users = self._alive_users_collection.check_expired_users()
        if len(expired_users) > 0:
            self._purge_expired_users(expired_users)

    @threaded(_resource_manager)
    def _purge_expired_users(self, expired_users):
        for expired_reservation in expired_users:
            if self._stopping:
                return
            try:
                expired_session = self._reservations_session_manager.get_session_locking(expired_reservation)
                try:
                    reservation = self._load_reservation(expired_session)
                    reservation.finish()
                finally:
                    self._reservations_session_manager.modify_session_unlocking(expired_reservation, expired_session)
            except Exception as e:
                log.log( UserProcessingServer, log.level.Error,
                    "Exception freeing experiment of %s: %s" % (expired_reservation, e))
                log.log_exc( UserProcessingServer, log.level.Warning)

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
            'latest_timestamp'    : 0 # epoch
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

            user_processor = self._load_user(session)

            reservation_id = session.get('reservation_id')
            if reservation_id is not None and not user_processor.is_access_forward_enabled():
                #
                # If "is_access_forward_enabled", the user (or more commonly, entity) can log out without
                # finishing his current reservation
                #
                # Furthermore, whenever booking is supported, this whole idea should be taken out. Even
                # with queues it might not make sense, depending on the particular type of experiment.
                #
                reservation_session = self._reservations_session_manager.get_session(SessionId(reservation_id))
                reservation_processor = self._load_reservation(reservation_session)
                reservation_processor.finish()
                self._alive_users_collection.remove_user(reservation_id)

            user_processor.logout()
            user_processor.update_latest_timestamp()

            self._session_manager.delete_session(session_id)
        else:
            raise coreExc.SessionNotFoundException( "User Processing Server session not found")


    @logged(log.level.Info)
    @update_session_id
    @check_session(**check_session_params)
    @load_user_processor
    def list_experiments(self, user_processor, session):
        return user_processor.list_experiments()


    @logged(log.level.Info)
    @update_session_id
    @check_session(**check_session_params)
    @load_user_processor
    def get_user_information(self, user_processor, session):
        return user_processor.get_user_information()

    # # # # # # # # # # # # # # # # #
    # Experiment related operations #
    # # # # # # # # # # # # # # # # #

    @logged(log.level.Info)
    @update_session_id
    @check_session(**check_session_params)
    @load_user_processor
    def reserve_experiment(self, user_processor, session, experiment_id, client_initial_data, consumer_data, client_address):
        status = user_processor.reserve_experiment( experiment_id, client_initial_data, consumer_data, client_address,
                                        self.core_server_universal_id)

        if status == 'replicated':
            return Reservation.NullReservation()

        reservation_id         = status.reservation_id.split(';')[0]
        reservation_session_id = SessionId(reservation_id)

        self._alive_users_collection.add_user(reservation_session_id)

        session_id = self._reservations_session_manager.create_session(reservation_id)

        initial_session = {
                        'session_polling'    : (time.time(), ReservationProcessor.EXPIRATION_TIME_NOT_SET),
                        'latest_timestamp'   : 0,
                        'experiment_id'      : experiment_id,
                        'creator_session_id' : session['session_id'], # Useful for monitor; should not be used
                        'reservation_id'     : reservation_session_id,
                    }
        reservation_processor = self._load_reservation(initial_session)
        reservation_processor.update_latest_timestamp()

        if status.status == WebLabSchedulingStatus.WebLabSchedulingStatus.RESERVED_LOCAL:
            reservation_processor.process_reserved_status(status)

        self._reservations_session_manager.modify_session(session_id, initial_session)
        return Reservation.Reservation.translate_reservation( status )


    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def finished_experiment(self, reservation_processor, session):
        reservation_session_id = reservation_processor.get_reservation_session_id()
        self._alive_users_collection.remove_user(reservation_session_id)
        return reservation_processor.finish()


    @logged(log.level.Info, except_for=(('file_content',2),))
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def send_file(self, reservation_processor, session, file_content, file_info):
        """ send_file(session_id, file_content, file_info)

        Sends file to the experiment.
        """
        self._check_reservation_not_expired_and_poll( reservation_processor )
        return reservation_processor.send_file( file_content, file_info )


    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def send_command(self, reservation_processor, session, command):
        """ send_command(session_id, command)

        send_command sends an abstract string <command> which will be unpacked by the
        experiment.
        """
        self._check_reservation_not_expired_and_poll( reservation_processor )
        return reservation_processor.send_command( command )

    @logged(log.level.Info, except_for=(('file_content',2),))
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def send_async_file(self, reservation_processor, session, file_content, file_info):
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
        self._check_reservation_not_expired_and_poll( reservation_processor )
        return reservation_processor.send_async_file( file_content, file_info )

    # TODO: This method should now be finished. Will need to be verified, though.
    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def check_async_command_status(self, reservation_processor, session, request_identifiers):
        """
        check_async_command_status(session_id, request_identifiers)
        Checks the status of several asynchronous commands.

        @param session: Session id
        @param request_identifiers: A list of the request identifiers of the
        requests to check.
        @return: Dictionary by request-id of the tuples: (status, content)
        """
        self._check_reservation_not_expired_and_poll( reservation_processor )
        return reservation_processor.check_async_command_status( request_identifiers )

    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def send_async_command(self, reservation_processor, session, command):
        """
        send_async_command(session_id, command)

        send_async_command sends an abstract string <command> which will be unpacked by the
        experiment, and run asynchronously on its own thread. Its status may be checked through
        check_async_command_status.
        """
        self._check_reservation_not_expired_and_poll( reservation_processor )
        return reservation_processor.send_async_command( command )

    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def get_reservation_info(self, reservation_processor, session):
        return reservation_processor.get_info()


    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    def poll(self, session):
        reservation_processor = self._load_reservation(session)
        self._check_reservation_not_expired_and_poll( reservation_processor )


    @logged(log.level.Info)
    @check_session(**check_reservation_session_params)
    @load_reservation_processor
    def get_reservation_status(self, reservation_processor, session):
        self._check_reservation_not_expired_and_poll( reservation_processor, False )
        return reservation_processor.get_status()

    ######################################
    #
    #  Admin services
    #
    #

    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_groups(self, user_processor, session, parent_id=None):
        return user_processor.get_groups(parent_id)


    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_experiments(self, user_processor, session):
        return user_processor.get_experiments()


    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_experiment_uses(self, user_processor, session, from_date=None, to_date=None, group_id=None, experiment_id=None, start_row=None, end_row=None, sort_by=None):
        return user_processor.get_experiment_uses(from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)

    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_experiment_use_by_id(self, user_processor, session, reservation_id):
        return user_processor.get_experiment_use_by_id(reservation_id)

    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_experiment_uses_by_id(self, user_processor, session, reservation_ids):
        return user_processor.get_experiment_uses_by_id(reservation_ids)

    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_roles(self, user_processor, session):
        return user_processor.get_roles()


    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_users(self, user_processor, session):
        """
        get_users(user_processor, session)

        Receives the get_users petition sent by the client and handles the request through
        a user processor for the calling session.

        @param user_processor UserProcessor object through which to handle the request
        @param session Session string
        @return List of users and their data
        """
        return user_processor.get_users()


    @logged(log.level.Info)
    @check_session(**check_session_params)
    @load_user_processor
    def get_user_permissions(self, user_processor, session):
        return user_processor.get_user_permissions()

