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
import time
import datetime

import json

from voodoo.typechecker import typecheck, ITERATION
from voodoo.log import logged
import voodoo.log as log
from voodoo.sessions.session_id import SessionId

from weblab.data.experiments import ExperimentId, ExperimentInstanceId

import weblab.core.coordinator.exc as CoordExc

import weblab.core.coordinator.sql.db as CoordinationDatabaseManager
import weblab.core.coordinator.sql.resource_manager as ResourcesManager
import weblab.core.coordinator.sql.reservations_manager as ReservationsManager
import weblab.core.coordinator.sql.post_reservation as PostReservationDataManager
import weblab.core.coordinator.confirmer as Confirmer

from weblab.core.coordinator.sql.meta_scheduler import IndependentSchedulerAggregator
from weblab.core.coordinator.sql.no_scheduler import NoScheduler
from weblab.core.coordinator.sql.priority_queue_scheduler import PriorityQueueScheduler
from weblab.core.coordinator.externals.weblabdeusto_scheduler import ExternalWebLabDeustoScheduler
from weblab.core.coordinator.externals.ilab_batch_scheduler import ILabBatchScheduler
from weblab.core.coordinator.resource import Resource

from weblab.core.coordinator.coordinator import AbstractCoordinator
from weblab.core.coordinator.coordinator import FINISH_FINISHED_MESSAGE, FINISH_DATA_MESSAGE, FINISH_ASK_AGAIN_MESSAGE
from weblab.core.coordinator.coordinator import  NO_SCHEDULER, PRIORITY_QUEUE, EXTERNAL_WEBLAB_DEUSTO, ILAB_BATCH_QUEUE

class Coordinator(AbstractCoordinator):

    SCHEDULING_SYSTEMS = {
        NO_SCHEDULER           : NoScheduler,
        PRIORITY_QUEUE         : PriorityQueueScheduler,
        EXTERNAL_WEBLAB_DEUSTO : ExternalWebLabDeustoScheduler,
        ILAB_BATCH_QUEUE       : ILabBatchScheduler,
    }

    AGGREGATOR = IndependentSchedulerAggregator

    def __init__(self, locator, cfg_manager, ConfirmerClass = Confirmer.ReservationConfirmer):
        super(Coordinator, self).__init__(locator, cfg_manager, ConfirmerClass)


    def _initial_clean(self, coordination_configuration_parser):
        session = self._session_maker()
        try:
            external_servers_config = coordination_configuration_parser.parse_external_servers()
            for external_server_str in external_servers_config:
                for resource_type_name in external_servers_config[external_server_str]:
                    self.resources_manager.add_experiment_id(session, ExperimentId.parse(external_server_str), resource_type_name)

            session.commit()
        finally:
            session.close()

    def _initialize_managers(self):
        coordination_database_manager = CoordinationDatabaseManager.CoordinationDatabaseManager(self.cfg_manager)
        self._session_maker = coordination_database_manager.session_maker

        self.reservations_manager          = ReservationsManager.ReservationsManager(self._session_maker)
        self.resources_manager             = ResourcesManager.ResourcesManager(self._session_maker)
        self.post_reservation_data_manager = PostReservationDataManager.PostReservationDataManager(self._session_maker, self.time_provider)

    ###########################################################################
    #
    # General experiments and sessions management
    #
    @typecheck(basestring, ExperimentInstanceId, Resource)
    @logged()
    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id, resource):
        session = self._session_maker()
        try:
            self.resources_manager.add_experiment_instance_id(session, laboratory_coord_address, experiment_instance_id, resource)
            session.commit()
        finally:
            session.close()

    @typecheck(Resource, ITERATION(basestring))
    @logged()
    def mark_resource_as_broken(self, resource_instance, messages = []):
        scheduler = self._get_scheduler_per_resource(resource_instance)

        anything_changed = False
        session = self._session_maker()
        try:
            changed = scheduler.removing_current_resource_slot(session, resource_instance)
            anything_changed = anything_changed or changed

            changed = self.resources_manager.mark_resource_as_broken(session, resource_instance)
            anything_changed = anything_changed or changed
            if anything_changed:
                session.commit()
        finally:
            session.close()

        if anything_changed:
            log.log( Coordinator, log.level.Warning,
                    "Resource %s marked as broken: %r" % (resource_instance, messages) )

            if self.notifications_enabled:
                self._notify_experiment_status('broken', resource_instance, messages)

    @typecheck(Resource)
    @logged()
    def mark_resource_as_fixed(self, resource_instance):
        session = self._session_maker()
        try:
            anything_changed = self.resources_manager.mark_resource_as_fixed(session, resource_instance)
            if anything_changed:
                session.commit()
        finally:
            session.close()

        if anything_changed:
            log.log( Coordinator, log.level.Warning,
                    "Resource %s marked as fixed" % resource_instance )

            if self.notifications_enabled:
                self._notify_experiment_status('fixed', resource_instance)

    ################################################################
    #
    # Called when the Laboratory Server states that the experiment
    # was cleaned
    #
    @typecheck(basestring, basestring, (basestring, type(None)), ExperimentInstanceId, (basestring, type(None)), datetime.datetime, datetime.datetime)
    @logged()
    def confirm_resource_disposal(self, lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time):

        experiment_finished  = True
        information_to_store = None
        time_remaining       = 0.5 # Every half a second by default

        if experiment_response is None or experiment_response == 'ok' or experiment_response == '':
            pass # Default value
        else:
            try:
                response = json.loads(experiment_response)
                experiment_finished   = response.get(FINISH_FINISHED_MESSAGE, experiment_finished)
                time_remaining        = response.get(FINISH_ASK_AGAIN_MESSAGE, time_remaining)
                information_to_store  = response.get(FINISH_DATA_MESSAGE, information_to_store)
            except Exception as e:
                log.log( Coordinator, log.level.Error, "Could not parse experiment server finishing response: %s; %s" % (e, experiment_response) )
                log.log_exc( Coordinator, log.level.Warning )

        if not experiment_finished:
            time.sleep(time_remaining)
            # We just ignore the data retrieved, if any, and perform the query again
            self.confirmer.enqueue_free_experiment(lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id)
            return
        else:
            # Otherwise we mark it as finished
            self.post_reservation_data_manager.finish(reservation_id, json.dumps(information_to_store))
            # and we remove the resource
            session = self._session_maker()
            try:
                resource_instance = self.resources_manager.get_resource_instance_by_experiment_instance_id(experiment_instance_id)
                self.resources_manager.release_resource_instance(session, resource_instance)
                session.commit()
            finally:
                session.close()
                self.finished_store.put(reservation_id, information_to_store, initial_time, end_time)

            # It's done here so it's called often enough
            self.post_reservation_data_manager.clean_expired()


    ################################################################
    #
    # Called when the user disconnects or finishes the experiment.
    #
    @typecheck(basestring)
    @logged()
    def finish_reservation(self, reservation_id):
        reservation_id = reservation_id.split(';')[0]
        if self.reservations_manager.initialize_deletion(reservation_id):
            self.finished_reservations_store.put(SessionId(reservation_id))
            try:
                aggregator = self._get_scheduler_aggregator_per_reservation(reservation_id)
                aggregator.finish_reservation(reservation_id)
                # The reservations_manager must remove the session once (not once per scheduler)
                session = self._session_maker()
                try:
                    self.reservations_manager.delete(session, reservation_id)
                    session.commit()
                finally:
                    session.close()
            except CoordExc.ExpiredSessionError:
                log.log(Coordinator, log.level.Info, "Ignore finish_reservation(%r), given that it had already expired" % reservation_id)
            finally:
                self.reservations_manager.clean_deletion(reservation_id)

    def _clean(self):
        for scheduler in self.schedulers.values():
            scheduler._clean()

        self.reservations_manager._clean()
        self.resources_manager._clean()
        self.post_reservation_data_manager._clean()

