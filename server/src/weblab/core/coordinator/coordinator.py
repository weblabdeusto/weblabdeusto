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
import Queue

import voodoo.admin_notifier as AdminNotifier

from weblab.data.experiments import ExperimentId

import weblab.core.coordinator.exc as CoordExc
import weblab.core.coordinator.scheduler as Scheduler
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.coordinator.config_parser as CoordinationConfigurationParser
import weblab.core.coordinator.confirmer as Confirmer
import weblab.core.coordinator.checker_threaded as ResourcesCheckerThread

FINISH_FINISHED_MESSAGE = 'finished'
FINISH_DATA_MESSAGE      = 'data'
FINISH_ASK_AGAIN_MESSAGE = 'ask_again'

POST_RESERVATION_EXPIRATION_TIME = 'core_post_reservation_expiration_time'
DEFAULT_POST_RESERVATION_EXPIRATION_TIME = 24 * 3600 # 1 day


NO_SCHEDULER           = 'NO_SCHEDULER'
PRIORITY_QUEUE         = 'PRIORITY_QUEUE'
EXTERNAL_WEBLAB_DEUSTO = 'EXTERNAL_WEBLAB_DEUSTO'
ILAB_BATCH_QUEUE       = 'ILAB_BATCH_QUEUE'

RESOURCES_CHECKER_NOTIFICATIONS_ENABLED = 'core_resources_checker_notifications_enabled'
DEFAULT_RESOURCES_CHECKER_NOTIFICATIONS_ENABLED = False

CORE_SCHEDULING_SYSTEMS    = 'core_scheduling_systems'
CORE_SCHEDULER_AGGREGATORS = 'core_scheduler_aggregators'
CORE_SERVER_URL            = 'core_server_url'

RESOURCES_CHECKER_FREQUENCY = 'core_resources_checker_frequency'
DEFAULT_RESOURCES_CHECKER_FREQUENCY = 30 # seconds

RESOURCES_CHECKER_GENERAL_RECIPIENTS = 'core_resources_checker_general_recipients'
DEFAULT_RESOURCES_GENERAL_CHECKER_RECIPIENTS = ()

RESOURCES_CHECKER_PARTICULAR_RECIPIENTS = 'core_resources_checker_particular_recipients'
DEFAULT_RESOURCES_PARTICULAR_CHECKER_RECIPIENTS = {
            # "inst1:ud-pld@PLD Experiments" : ['admin1@whatever.edu', 'admin2@whatever.edu']
        }

class TimeProvider(object):
    def get_time(self):
        return time.time()

    def get_datetime(self):
        return datetime.datetime.utcnow()


class AbstractCoordinator(object):
    CoordinatorTimeProvider = TimeProvider

    def __init__(self, locator, cfg_manager, ConfirmerClass = Confirmer.ReservationConfirmer):

        self.cfg_manager = cfg_manager

        self.core_server_url = self.cfg_manager.get_value(CORE_SERVER_URL)

        self.notifier = AdminNotifier.AdminNotifier(self.cfg_manager)
        self.notifications_enabled = self.cfg_manager.get_value(RESOURCES_CHECKER_NOTIFICATIONS_ENABLED, DEFAULT_RESOURCES_CHECKER_NOTIFICATIONS_ENABLED)

        self.locator   = locator # Used by ResourcesChecker
        self.confirmer = ConfirmerClass(self, locator)

        self.time_provider = self.CoordinatorTimeProvider()

        self.initial_store  = TemporalInformationStore.InitialTemporalInformationStore()
        self.finished_store = TemporalInformationStore.FinishTemporalInformationStore()
        self.completed_store = TemporalInformationStore.CompletedInformationStore()
        self.finished_reservations_store = Queue.Queue()


        self._initialize_managers()

        #
        # The system administrator must define what scheduling system is used by each resource type
        # For instance:
        #
        # scheduling_systems = {
        #                  "pld boards"     : ("PRIORITY_QUEUE", {}),
        #                  "fpga boards"    : ("PRIORITY_QUEUE", {}),
        #                  "vm experiments" : ("BOOKING", { 'slots' : 30 * 1000 }), # Slots of 30 minutes
        #                  "something else" : ("EXTERNAL", { 'address' : 'http://192.168.1.50:8080/SchedulingServer', 'protocol' : 'SOAP' }) # If somebody else has implemented the scheduling schema in other language
        #            }
        #
        self.schedulers = {}
        scheduling_systems = cfg_manager.get_value(CORE_SCHEDULING_SYSTEMS)
        for resource_type_name in scheduling_systems:
            scheduling_system, arguments = scheduling_systems[resource_type_name]
            if not scheduling_system in self.SCHEDULING_SYSTEMS:
                raise CoordExc.UnregisteredSchedulingSystemError("Unregistered scheduling system: %r" % scheduling_system)
            SchedulingSystemClass = self.SCHEDULING_SYSTEMS[scheduling_system]

            generic_scheduler_arguments = Scheduler.GenericSchedulerArguments(
                                                cfg_manager          = self.cfg_manager,
                                                resource_type_name   = resource_type_name,
                                                reservations_manager = self.reservations_manager,
                                                resources_manager    = self.resources_manager,
                                                confirmer            = self.confirmer,
                                                session_maker        = self._session_maker,
                                                time_provider        = self.time_provider,
                                                core_server_url      = self.core_server_url,
                                                initial_store        = self.initial_store,
                                                finished_store       = self.finished_store,
                                                completed_store      = self.completed_store,
                                                post_reservation_data_manager = self.post_reservation_data_manager
                                        )

            self.schedulers[resource_type_name] = SchedulingSystemClass(generic_scheduler_arguments, **arguments)

        self.aggregators = {
            # experiment_id_str : AGGREGATOR( schedulers )
        }

        coordination_configuration_parser = CoordinationConfigurationParser.CoordinationConfigurationParser(cfg_manager)
        resource_types_per_experiment_id = coordination_configuration_parser.parse_resources_for_experiment_ids()

        #
        # This configuration argument has a dictionary such as:
        # {
        #     'experiment_id_str' : {'foo' : 'bar'}
        # }
        #
        # The argument itself is not mandatory.
        #
        aggregators_configuration = self.cfg_manager.get_value(CORE_SCHEDULER_AGGREGATORS, {})

        for experiment_id_str in resource_types_per_experiment_id:
            generic_scheduler_arguments = Scheduler.GenericSchedulerArguments(
                                                cfg_manager          = self.cfg_manager,
                                                resource_type_name   = None,
                                                reservations_manager = self.reservations_manager,
                                                resources_manager    = self.resources_manager,
                                                confirmer            = self.confirmer,
                                                session_maker        = self._session_maker,
                                                time_provider        = self.time_provider,
                                                core_server_url      = self.core_server_url,
                                                initial_store        = self.initial_store,
                                                finished_store       = self.finished_store,
                                                completed_store      = self.completed_store,
                                                post_reservation_data_manager = self.post_reservation_data_manager
                                        )


            resource_type_names = resource_types_per_experiment_id[experiment_id_str]
            try:
                aggregated_schedulers = {}
                for resource_type_name in resource_type_names:
                    aggregated_schedulers[resource_type_name] = self.schedulers[resource_type_name]

            except KeyError, ke:
                raise Exception("Scheduler not found with resource type name %s. Check %s config property." % (ke, CORE_SCHEDULING_SYSTEMS))

            particular_configuration = aggregators_configuration.get(experiment_id_str)

            aggregator = self.AGGREGATOR(generic_scheduler_arguments, ExperimentId.parse(experiment_id_str), aggregated_schedulers, particular_configuration)

            self.aggregators[experiment_id_str] = aggregator


        import weblab.core.server as UserProcessingServer
        clean = cfg_manager.get_value(UserProcessingServer.WEBLAB_CORE_SERVER_CLEAN_COORDINATOR, True)

        post_reservation_expiration_time = cfg_manager.get_value(POST_RESERVATION_EXPIRATION_TIME, DEFAULT_POST_RESERVATION_EXPIRATION_TIME)
        self.expiration_delta = datetime.timedelta(seconds=post_reservation_expiration_time)

        if clean:
            resources_checker_frequency = cfg_manager.get_value(RESOURCES_CHECKER_FREQUENCY, DEFAULT_RESOURCES_CHECKER_FREQUENCY)
            ResourcesCheckerThread.set_coordinator(self, resources_checker_frequency)

            self._clean()

            coordination_configuration_parser = CoordinationConfigurationParser.CoordinationConfigurationParser(self.cfg_manager)

            configuration = coordination_configuration_parser.parse_configuration()
            for laboratory_server_coord_address_str in configuration:
                experiment_instance_config = configuration[laboratory_server_coord_address_str]
                for experiment_instance_id in experiment_instance_config:
                    resource = experiment_instance_config[experiment_instance_id]
                    self.add_experiment_instance_id(laboratory_server_coord_address_str, experiment_instance_id, resource)

            self._initial_clean(coordination_configuration_parser)



    def _initialize_managers(self): 
        pass

    def _initial_clean(self, coordination_configuration_parser):
        pass

    def _retrieve_recipients(self, experiment_instance_ids):
        recipients = ()
        server_admin = self.cfg_manager.get_value(AdminNotifier.SERVER_ADMIN_NAME, None)
        if server_admin is not None:
            if server_admin.find(","):
                server_admins = tuple(server_admin.replace(" ","").split(","))
            else:
                server_admins = (server_admin,)
            recipients += server_admins

        general_recipients = self.cfg_manager.get_value(RESOURCES_CHECKER_GENERAL_RECIPIENTS, DEFAULT_RESOURCES_GENERAL_CHECKER_RECIPIENTS)
        recipients += tuple(general_recipients)

        for experiment_instance_id in experiment_instance_ids:
            particular_recipients = self.cfg_manager.get_value(RESOURCES_CHECKER_PARTICULAR_RECIPIENTS, DEFAULT_RESOURCES_PARTICULAR_CHECKER_RECIPIENTS)
            experiment_particular_recipients = particular_recipients.get(experiment_instance_id.to_weblab_str(), ())
            recipients += tuple(experiment_particular_recipients)

        return tuple(set(recipients))
