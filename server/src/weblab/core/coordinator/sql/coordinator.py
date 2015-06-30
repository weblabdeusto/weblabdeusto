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

from voodoo.typechecker import typecheck, ITERATION
from voodoo.log import logged
import voodoo.log as log

from weblab.data.experiments import ExperimentId

import weblab.core.coordinator.sql.db as CoordinationDatabaseManager
import weblab.core.coordinator.sql.resource_manager as ResourcesManager
import weblab.core.coordinator.sql.reservations_manager as ReservationsManager
import weblab.core.coordinator.sql.post_reservation as PostReservationDataManager

from weblab.core.coordinator.sql.meta_scheduler import IndependentSchedulerAggregator
from weblab.core.coordinator.sql.no_scheduler import NoScheduler
from weblab.core.coordinator.sql.priority_queue_scheduler import PriorityQueueScheduler
from weblab.core.coordinator.sql.externals.weblabdeusto_scheduler import ExternalWebLabDeustoScheduler
from weblab.core.coordinator.sql.externals.ilab_batch_scheduler import ILabBatchScheduler
from weblab.core.coordinator.resource import Resource

from weblab.core.coordinator.coordinator import AbstractCoordinator
from weblab.core.coordinator.coordinator import  NO_SCHEDULER, PRIORITY_QUEUE, EXTERNAL_WEBLAB_DEUSTO, ILAB_BATCH_QUEUE

class Coordinator(AbstractCoordinator):

    SCHEDULING_SYSTEMS = {
        NO_SCHEDULER           : NoScheduler,
        PRIORITY_QUEUE         : PriorityQueueScheduler,
        EXTERNAL_WEBLAB_DEUSTO : ExternalWebLabDeustoScheduler,
        ILAB_BATCH_QUEUE       : ILabBatchScheduler,
    }

    AGGREGATOR = IndependentSchedulerAggregator

    def __init__(self, locator, cfg_manager, ConfirmerClass = None):
        coordination_database_manager = CoordinationDatabaseManager.CoordinationDatabaseManager(cfg_manager)
        self._session_maker = coordination_database_manager.session_maker
        super(Coordinator, self).__init__(self._session_maker, locator, cfg_manager, ConfirmerClass)


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
        self.reservations_manager          = ReservationsManager.ReservationsManager(self._session_maker)
        self.resources_manager             = ResourcesManager.ResourcesManager(self._session_maker)
        self.post_reservation_data_manager = PostReservationDataManager.PostReservationDataManager(self._session_maker, self.time_provider)

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
                return self._notify_experiment_status('broken', resource_instance, messages)
        return {}

    def _release_resource_instance(self, experiment_instance_id):
        session = self._session_maker()
        try:
            resource_instance = self.resources_manager.get_resource_instance_by_experiment_instance_id(experiment_instance_id)
            self.resources_manager.release_resource_instance(session, resource_instance)
            session.commit()
        finally:
            session.close()

    def _delete_reservation(self, reservation_id):
        session = self._session_maker()
        try:
            self.reservations_manager.delete(session, reservation_id)
            session.commit()
        finally:
            session.close()

    def _clean(self):
        for scheduler in self.schedulers.values():
            scheduler._clean()

        self.reservations_manager._clean()
        self.resources_manager._clean()
        self.post_reservation_data_manager._clean()

