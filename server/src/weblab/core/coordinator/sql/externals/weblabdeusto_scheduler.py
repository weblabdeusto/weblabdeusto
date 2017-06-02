#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import time as time_mod
import cPickle as pickle
import json
import datetime

from sqlalchemy.orm.exc import StaleDataError

import voodoo.log as log
from voodoo.override import Override
from voodoo.sessions.session_id import SessionId

from weblab.data.experiments import ExperimentId

from weblab.core.user_processor import FORWARDED_KEYS, SERVER_UUIDS
import weblab.core.coordinator.status as WSS
from weblab.core.coordinator.scheduler import Scheduler
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.core.coordinator.sql.externals.weblabdeusto_scheduler_model import ExternalWebLabDeustoReservation, ExternalWebLabDeustoReservationPendingResults

from weblab.core.coordinator.sql.externals.weblabdeusto_scheduler_retriever import ResultsRetriever
from voodoo.log import logged

RETRIEVAL_PERIOD_PROPERTY_NAME = 'core_weblabdeusto_federation_retrieval_period'
DEFAULT_RETRIEVAL_PERIOD = 10


class ExternalWebLabDeustoScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, baseurl, username, password, login_baseurl = None, experiments_map = None, uuid = None, **kwargs):
        super(ExternalWebLabDeustoScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

        self.baseurl       = baseurl
        self.login_baseurl = login_baseurl
        self.username      = username
        self.password      = password
        if experiments_map is None:
            self.experiments_map = {}
        else:
            self.experiments_map = experiments_map
        if uuid is None:
            self.uuids = []
        elif isinstance(uuid, basestring):
            human = baseurl
            self.uuids = [ (uuid, human) ]
        else:
            self.uuids = [uuid]

        from weblab.core.coordinator.coordinator import POST_RESERVATION_EXPIRATION_TIME, DEFAULT_POST_RESERVATION_EXPIRATION_TIME
        post_reservation_expiration_time = self.cfg_manager.get_value(POST_RESERVATION_EXPIRATION_TIME, DEFAULT_POST_RESERVATION_EXPIRATION_TIME)
        self.expiration_delta = datetime.timedelta(seconds=post_reservation_expiration_time)

        period = self.cfg_manager.get_value(RETRIEVAL_PERIOD_PROPERTY_NAME, DEFAULT_RETRIEVAL_PERIOD)
        self.retriever     = ResultsRetriever(self, period, self._create_logged_in_client)
        self.retriever.start()

    def stop(self):
        self.retriever.stop()

    @Override(Scheduler)
    def is_remote(self):
        return True

    @Override(Scheduler)
    def get_uuids(self):
        return self.uuids

    @logged()
    @Override(Scheduler)
    def removing_current_resource_slot(self, session, resource_instance_id):
        # Will in fact never be called
        return False

    # TODO: pooling
    def _create_client(self, cookies = None):
        client = WebLabDeustoClient(self.baseurl)
        if cookies is not None:
            client.set_cookies(cookies)
        return client

    def _create_login_client(self, cookies = None):
        client = WebLabDeustoClient(self.login_baseurl or self.baseurl)
        if cookies is not None:
            client.set_cookies(cookies)
        return client

    def _create_logged_in_client(self, cookies):
        login_client = self._create_login_client(cookies)
        session_id = login_client.login(self.username, self.password)
        client = self._create_client(login_client.get_cookies())
        return session_id, client


    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info):
        server_uuids = list(request_info.get(SERVER_UUIDS, []))
        server_uuids.append((self.core_server_uuid, self.core_server_uuid_human))

        consumer_data = {
            'time_allowed'                 : time,
            'priority'                     : priority,
            'initialization_in_accounting' : initialization_in_accounting,
            'external_user'                : request_info.get('username', ''),
            SERVER_UUIDS                   : server_uuids,
        }

        for forwarded_key in FORWARDED_KEYS:
            if forwarded_key in request_info:
                consumer_data[forwarded_key] = request_info[forwarded_key]

        consumer_data['external_user_unique'] = request_info.get('username_unique', request_info.get('username', ''))

        # TODO: identifier of the server
        login_client = self._create_login_client()
        session_id = login_client.login(self.username, self.password)

        client = self._create_client(login_client.get_cookies())

        serialized_client_initial_data = json.dumps(client_initial_data)
        serialized_consumer_data       = json.dumps(consumer_data)
        # If the administrator has mapped that this experiment_id is other, take that other. Otherwide, take the same one
        requested_experiment_id_str    = self.experiments_map.get(experiment_id.to_weblab_str(), experiment_id.to_weblab_str())
        requested_experiment_id        = ExperimentId.parse(requested_experiment_id_str)
        external_reservation = client.reserve_experiment(session_id, requested_experiment_id, serialized_client_initial_data, serialized_consumer_data)

        if external_reservation.is_null():
            return None

        remote_reservation_id = external_reservation.reservation_id.id
        log.log(ExternalWebLabDeustoScheduler, log.level.Info, "Local reservation_id %s is linked to remote reservation %s" % (reservation_id, remote_reservation_id))

        cookies = client.get_cookies()
        serialized_cookies = pickle.dumps(cookies)

        session = self.session_maker()
        try:
            reservation = ExternalWebLabDeustoReservation(reservation_id, remote_reservation_id, serialized_cookies, time_mod.time())
            pending_results = ExternalWebLabDeustoReservationPendingResults(reservation_id, remote_reservation_id, self.resource_type_name, self.core_server_route, request_info.get('username', ''), pickle.dumps(request_info), experiment_id.to_weblab_str())
            session.add(reservation)
            session.add(pending_results)
            session.commit()
        finally:
            session.close()

        reservation_status = self._convert_reservation_to_status(external_reservation, reservation_id, remote_reservation_id)
        return reservation_status

    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):

        reservation_found = False
        max_iterations = 15

        while not reservation_found and max_iterations >= 0:
            session = self.session_maker()
            try:
                reservation = session.query(ExternalWebLabDeustoReservation).filter_by(local_reservation_id = reservation_id).first()
                if reservation is None:
                    pending_result = session.query(ExternalWebLabDeustoReservationPendingResults).filter_by(resource_type_name = self.resource_type_name, server_route = self.core_server_route, reservation_id = reservation_id).first()
                    if pending_result is None:
                        # reservation not yet stored in local database
                        pass
                    else:
                        return WSS.PostReservationStatus(reservation_id, False, '', '')
                else:
                    reservation_found = True
                    remote_reservation_id = reservation.remote_reservation_id
                    serialized_cookies    = reservation.cookies
            finally:
                session.close()
            
            # Introduce a delay to let the system store the reservation in the local database
            if not reservation_found:
                time_mod.sleep(0.1)
                max_iterations -= 1

        if not reservation_found:
            return WSS.PostReservationStatus(reservation_id, False, '', '')

        cookies = pickle.loads(str(serialized_cookies))
        client = self._create_client(cookies)

        reservation = client.get_reservation_status(SessionId(remote_reservation_id))

        return self._convert_reservation_to_status(reservation, reservation_id, remote_reservation_id)

    def _convert_reservation_to_status(self, reservation, local_reservation_id, remote_reservation_id):
        reservation_status = reservation.to_status()
        reservation_status.set_reservation_id(local_reservation_id)
        if reservation_status.status == WSS.WebLabSchedulingStatus.RESERVED_REMOTE:
            # 
            # If it has been successfully reserved in a remote server, it can mean two things:
            # 
            #  a) the remote_reservation_id can be empty, and therefore the remote server we're 
            #     contacting is the one with the resource
            #  
            #  b) the remote_reservation_id is other address, and therefore the remote server is
            #     proxying the communications another server
            # 
            # We have to change the remote reservation id if it is empty
            # 
            if reservation_status.remote_reservation_id == '':
                reservation_status.set_remote_reservation_id(remote_reservation_id)

        reservation_id_with_route = '%s;%s.%s' % (local_reservation_id, local_reservation_id, self.core_server_route)
        reservation_status.reservation_id = reservation_id_with_route

        return reservation_status



    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration, exp_info):
        # At some point, we must call the upper level to say that we want to confirm
        # at this point, it's normal that they call us back, even if there is nothing
        # to do
        pass

    ################################################################
    #
    # Called when the user disconnects or finishes the resource.
    #
    @logged()
    @Override(Scheduler)
    def finish_reservation(self, reservation_id):
        session = self.session_maker()
        try:
            reservation = session.query(ExternalWebLabDeustoReservation).filter_by(local_reservation_id = reservation_id).first()
            if reservation is not None:
                remote_reservation_id = reservation.remote_reservation_id
                serialized_cookies = reservation.cookies
            else:
                log.log(ExternalWebLabDeustoScheduler, log.level.Info, "Not finishing reservation %s since somebody already did it" % reservation_id)
                return
        finally:
            session.close()

        cookies = pickle.loads(str(serialized_cookies))
        client = self._create_client(cookies)
        client.finished_experiment(SessionId(remote_reservation_id))
        try:
            client.get_reservation_status(SessionId(remote_reservation_id))
        except:
            # TODO: Actually check that the reservation was expired
            pass # Expired reservation
        else:
            now = self.time_provider.get_datetime()
            self.post_reservation_data_manager.create(reservation_id, now, now + self.expiration_delta, json.dumps("''"))

        session = self.session_maker()
        try:
            reservation = session.query(ExternalWebLabDeustoReservation).filter_by(local_reservation_id = reservation_id).first()
            if reservation is not None:
                try:
                    session.delete(reservation)
                    session.commit()
                except StaleDataError:
                    log.log(ExternalWebLabDeustoScheduler, log.level.Info, "Could not remove reservation_id %s from ExternalWebLabDeustoReservation since somebody already did it" % reservation_id)
            else:
                log.log(ExternalWebLabDeustoScheduler, log.level.Info, "Not deleting reservation %s from ExternalWebLabDeustoReservation since somebody already did it" % reservation_id)
                return
        finally:
            session.close()


    ##############################################################
    #
    # ONLY FOR TESTING: It completely removes the whole database
    #
    @Override(Scheduler)
    def _clean(self):
        session = self.session_maker()

        try:
            for reservation in session.query(ExternalWebLabDeustoReservation).all():
                session.delete(reservation)
            for pending_reservation in session.query(ExternalWebLabDeustoReservationPendingResults).all():
                session.delete(pending_reservation)
            session.commit()
        finally:
            session.close()

