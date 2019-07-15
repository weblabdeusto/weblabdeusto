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

try:
    import redis
except ImportError:
    REDIS_AVAILABLE = False
else:
    REDIS_AVAILABLE = True

from voodoo.typechecker import typecheck, ITERATION
from voodoo.log import logged
import voodoo.log as log

from weblab.data.experiments import ExperimentId

import weblab.core.coordinator.redis.resource_manager as ResourcesManager
import weblab.core.coordinator.redis.reservations_manager as ReservationsManager
import weblab.core.coordinator.redis.post_reservation as PostReservationDataManager

from weblab.core.coordinator.redis.meta_scheduler import IndependentSchedulerAggregator
from weblab.core.coordinator.redis.no_scheduler import NoScheduler
from weblab.core.coordinator.redis.priority_queue_scheduler import PriorityQueueScheduler
from weblab.core.coordinator.redis.externals.weblabdeusto_scheduler import ExternalWebLabDeustoScheduler
from weblab.core.coordinator.redis.externals.ilab_batch_scheduler import ILabBatchScheduler
from weblab.core.coordinator.resource import Resource

from weblab.core.coordinator.coordinator import AbstractCoordinator
from weblab.core.coordinator.coordinator import  NO_SCHEDULER, PRIORITY_QUEUE, EXTERNAL_WEBLAB_DEUSTO, ILAB_BATCH_QUEUE

COORDINATOR_REDIS_DB       = 'coordinator_redis_db'
COORDINATOR_REDIS_PASSWORD = 'coordinator_redis_password'
COORDINATOR_REDIS_PORT     = 'coordinator_redis_port'
COORDINATOR_REDIS_HOST     = 'coordinator_redis_host'

class Coordinator(AbstractCoordinator):

    SCHEDULING_SYSTEMS = {
        NO_SCHEDULER           : NoScheduler,
        PRIORITY_QUEUE         : PriorityQueueScheduler,
        EXTERNAL_WEBLAB_DEUSTO : ExternalWebLabDeustoScheduler,
        ILAB_BATCH_QUEUE       : ILabBatchScheduler,
    }

    AGGREGATOR = IndependentSchedulerAggregator

    def __init__(self, locator, cfg_manager, ConfirmerClass = None):
        connection_kwargs = {}
        db       = cfg_manager.get_value(COORDINATOR_REDIS_DB,       None)
        password = cfg_manager.get_value(COORDINATOR_REDIS_PASSWORD, None)
        port     = cfg_manager.get_value(COORDINATOR_REDIS_PORT,     None)
        host     = cfg_manager.get_value(COORDINATOR_REDIS_HOST,     None)
        if db is not None: 
            connection_kwargs['db']       = db
        if password is not None:
            connection_kwargs['password'] = password
        if port is not None:
            connection_kwargs['port']     = port
        if host is not None:
            connection_kwargs['host']     = host
        self.pool = redis.ConnectionPool(**connection_kwargs)
        self._redis_maker = lambda : redis.Redis(connection_pool = self.pool)

        super(Coordinator, self).__init__(self._redis_maker, locator, cfg_manager, ConfirmerClass)

    def stop(self):
        super(Coordinator, self).stop()

        self.pool.disconnect()

    def _initial_clean(self, coordination_configuration_parser):
        external_servers_config = coordination_configuration_parser.parse_external_servers()
        for external_server_str in external_servers_config:
            for resource_type_name in external_servers_config[external_server_str]:
                self.resources_manager.add_experiment_id(ExperimentId.parse(external_server_str), resource_type_name)

    def _initialize_managers(self):
        self.reservations_manager          = ReservationsManager.ReservationsManager(self._redis_maker)
        self.resources_manager             = ResourcesManager.ResourcesManager(self._redis_maker)
        self.post_reservation_data_manager = PostReservationDataManager.PostReservationDataManager(self._redis_maker, self.time_provider)

    @typecheck(Resource, ITERATION(basestring))
    @logged()
    def mark_resource_as_broken(self, resource_instance, messages = []):
        scheduler = self._get_scheduler_per_resource(resource_instance)

        anything_changed = False
        client = self._redis_maker()
        changed = scheduler.removing_current_resource_slot(client, resource_instance)
        anything_changed = anything_changed or changed

        changed = self.resources_manager.mark_resource_as_broken(resource_instance, messages)
        anything_changed = anything_changed or changed

        if anything_changed:
            log.log( Coordinator, log.level.Warning,
                    "Resource %s marked as broken: %r" % (resource_instance, messages) )

            if self.notifications_enabled:
                return self._notify_experiment_status('broken', resource_instance, messages)
        return {}

    def _release_resource_instance(self, experiment_instance_id):
        resource_instance = self.resources_manager.get_resource_instance_by_experiment_instance_id(experiment_instance_id)
        self.resources_manager.release_resource_instance(resource_instance)

    def _delete_reservation(self, reservation_id):
        self.reservations_manager.delete(reservation_id)

    def _clean(self):
        for scheduler in self.schedulers.values():
            scheduler._clean()

        self.reservations_manager._clean()
        self.resources_manager._clean()
        self.post_reservation_data_manager._clean()

