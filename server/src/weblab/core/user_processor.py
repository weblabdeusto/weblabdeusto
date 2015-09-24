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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import time as time_module
import json

import voodoo.log as log
from voodoo.typechecker import typecheck
from voodoo.sessions.session_id import SessionId

import weblab.configuration_doc as configuration_doc
from weblab.data.experiments import ExperimentUsage

import weblab.core.exc as core_exc
import weblab.core.coordinator.exc as coord_exc

from weblab.core.coordinator.status import WebLabSchedulingStatus

from weblab.data.experiments import RunningReservationResult, WaitingReservationResult, CancelledReservationResult, FinishedReservationResult, ForbiddenReservationResult

from weblab.core.wl import weblab_api

FORWARDED_KEYS = 'external_user','user_agent','referer','mobile','facebook','from_ip','locale'
SERVER_UUIDS   = 'server_uuid'

class UserProcessor(object):
    """
    User processors are linked to specific sessions. Requests that arrive to the
    UserProcessingManager will be told apart through their session_id and forwarded
    to the appropriate UserProcessor.
    """

    EXPIRATION_TIME_NOT_SET=-1234

    def __init__(self, locator, session, cfg_manager, coordinator, db_manager, commands_store):
        self._locator         = locator
        self._session         = session
        self._cfg_manager     = cfg_manager
        self._coordinator     = coordinator
        self._db_manager      = db_manager
        self._commands_store  = commands_store
        self._server_route    = cfg_manager.get_doc_value(configuration_doc.CORE_FACADE_SERVER_ROUTE)
        self.time_module      = time_module

    @property
    def username(self):
        return self._session['db_session_id'].username

    def list_experiments(self, exp_name = None, cat_name = None):
        return self._db_manager.list_experiments(self.username, exp_name = exp_name, cat_name = cat_name)

    def get_user_information(self):
        if 'user_information' in self._session:
            return self._session['user_information']

        user_information            = self._db_manager.get_user_by_name(self.username)
        self._session['user_information'] = user_information
        return user_information

    def get_session(self):
        return self._session

    def get_session_id(self):
        return self._session['session_id']

    def is_access_forward_enabled(self):
        return self._db_manager.is_access_forward(self.username)

    def is_admin(self):
        return self._db_manager.is_admin(self.username)

    def is_instructor(self):
        return self._db_manager.is_instructor(self.username)

    #
    # Experiments
    #

    def reserve_experiment(self, experiment_id, serialized_client_initial_data, serialized_consumer_data, client_address, core_server_universal_id ):

        # Put user information in the session
        self.get_user_information()

        self._session['experiment_id'] = experiment_id

        reservation_info = self._session['reservation_information'] = {}
        reservation_info['user_agent']     = weblab_api.user_agent
        reservation_info['referer']        = weblab_api.referer
        reservation_info['mobile']         = weblab_api.is_mobile
        reservation_info['locale']         = weblab_api.locale
        reservation_info['facebook']       = weblab_api.is_facebook
        reservation_info['route']          = self._server_route or 'no-route-found'
        reservation_info['username']       = self.username
        reservation_info['from_ip']        = client_address
        reservation_info['from_direct_ip'] = client_address
#        reservation_info['full_name']      = self._session['user_information'].full_name
        reservation_info['role']           = self._session['db_session_id'].role

        try:
            client_initial_data = json.loads(serialized_client_initial_data)
        except ValueError:
            # TODO: to be tested
            raise core_exc.WebLabCoreError( "Invalid client_initial_data provided: a json-serialized object expected" )

        if self.is_access_forward_enabled():
            try:
                consumer_data = json.loads(serialized_consumer_data)
                for forwarded_key in FORWARDED_KEYS:
                    if forwarded_key in consumer_data:
                        if consumer_data[forwarded_key] is not None:
                            reservation_info[forwarded_key] = consumer_data[forwarded_key]

                server_uuids = consumer_data.get(SERVER_UUIDS, [])
                for server_uuid, server_uuid_human in server_uuids:
                    if server_uuid == core_server_universal_id:
                        return 'replicated'
                reservation_info[SERVER_UUIDS] = server_uuids
            except ValueError:
                raise core_exc.WebLabCoreError( "Invalid serialized_consumer_data provided: a json-serialized object expected" )
        else:
            consumer_data = {}


        experiments = self._db_manager.list_experiments(self.username, experiment_id.exp_name, experiment_id.cat_name)

        if len(experiments) == 0:
            raise core_exc.UnknownExperimentIdError( "User can't access that experiment (or that experiment type does not exist)" )

        experiment_allowed = experiments[0]
        try:
            # Retrieve the most restrictive values between what was requested and what was permitted:
            #
            # The smallest time allowed
            time_allowed                 = min(experiment_allowed.time_allowed,                consumer_data.get('time_allowed', experiment_allowed.time_allowed))
            #
            # The lowest priority (lower number is higher)
            # TODO: whenever possible, there should be an argument in the permission as
            # a parameter to the access_forward, such as:
            # "how much you want to decrement the requested priority to this user"
            priority                     = max(experiment_allowed.priority,                    consumer_data.get('priority', experiment_allowed.priority))

            #
            # Don't take into account initialization unless both agree
            initialization_in_accounting = experiment_allowed.initialization_in_accounting and consumer_data.get('initialization_in_accounting', experiment_allowed.initialization_in_accounting)
            reservation_info['permission_scope'] = experiment_allowed.permission_scope
            reservation_info['permission_id']    = experiment_allowed.permission_id

            status, reservation_id    = self._coordinator.reserve_experiment(
                    experiment_allowed.experiment.to_experiment_id(),
                    time_allowed,
                    priority,
                    initialization_in_accounting,
                    client_initial_data,
                    reservation_info,
                    consumer_data
                )
        except coord_exc.ExperimentNotFoundError:
            raise core_exc.NoAvailableExperimentFoundError(
                "No experiment of type <%s,%s> is currently deployed" % (
                        experiment_id.exp_name,
                        experiment_id.cat_name
                    )
            )


        self._session['reservation_information'].pop('from_ip', None)
        self._session['reservation_id']   = reservation_id

        return status

    def logout(self):
        # self.finished_experiment()
        pass

    def update_latest_timestamp(self):
        self._session['latest_timestamp'] = self._utc_timestamp()

    def _utc_timestamp(self):
        return self.time_module.time()

    @typecheck(SessionId)
    def get_experiment_use_by_id(self, reservation_id):
        experiment_uses = self._db_manager.get_experiment_uses_by_id(self.username, [SessionId(reservation_id.id.split(';')[0])])
        experiment_use  = experiment_uses[0]
        return self._process_use(experiment_use, reservation_id)

    @typecheck(typecheck.ITERATION(SessionId))
    def get_experiment_uses_by_id(self, reservation_ids):
        experiment_uses = self._db_manager.get_experiment_uses_by_id(self.username, [SessionId(reservation_id.id.split(';')[0]) for reservation_id in reservation_ids])

        results = []
        cancelled_results = []
        for pos, (experiment_use, reservation_id) in enumerate(zip(experiment_uses, reservation_ids)):
            result = self._process_use(experiment_use, reservation_id)
            results.append(result)
            if result.is_cancelled():
                cancelled_results.append((pos, reservation_id))

        if len(cancelled_results) > 0:
            # Sometimes, the system recognizes as cancelled a reservation which was removed 
            # between the moment we asked for results and the moment we stored the results.
            # Just in case, we check again those results

            tentatively_cancelled_experiment_uses = self._db_manager.get_experiment_uses_by_id(self.username, [SessionId(reservation_id.id.split(';')[0]) for pos, reservation_id in cancelled_results])
            for (pos, reservation_id), tentatively_cancelled_use in zip(cancelled_results, tentatively_cancelled_experiment_uses):
                # Only process the use if the use is now not None
                if tentatively_cancelled_use is not None:
                    tentatively_cancelled_result = self._process_use(tentatively_cancelled_use, reservation_id)
                    if not tentatively_cancelled_result.is_cancelled():
                        # If it is not cancelled anymore, then we replace the previous value
                        results[pos] = tentatively_cancelled_result
            
        return results


    @typecheck((ExperimentUsage, basestring, typecheck.NONE), SessionId)
    def _process_use(self, use, reservation_id):
        """Given a reservation_id not present in the usage db, check if it is still running or waiting, or it did never enter the system"""
        if use is not None:
            if use == self._db_manager.forbidden_access:
                return ForbiddenReservationResult()
            if use.end_date is None:
                log.log(UserProcessor, log.level.Debug, "Reservation %s is running since end_time is None" % reservation_id)
                return RunningReservationResult()
            storage_path = self._cfg_manager.get_value('core_store_students_programs_path')
            use.load_files(storage_path)
            return FinishedReservationResult(use)

        try:
            # We don't actually care about the result. The question is: has it expired or is it running?
            status = self._coordinator.get_reservation_status(reservation_id.id)
            if status.status in WebLabSchedulingStatus.NOT_USED_YET_EXPERIMENT_STATUS:
                return WaitingReservationResult()
            else:
                log.log(UserProcessor, log.level.Debug, "Reservation %s is running due to status %r" % (reservation_id, status))
                return RunningReservationResult()
        except coord_exc.ExpiredSessionError, ese:
            log.log(UserProcessor, log.level.Debug, "Reservation %s is cancelled due to expired session: %s" % (reservation_id, ese))
            return CancelledReservationResult()

    def get_user_permissions(self):
        return self._db_manager.get_user_permissions(self.username)

