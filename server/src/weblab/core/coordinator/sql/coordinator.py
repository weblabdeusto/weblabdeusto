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
from voodoo.gen.coordinator.CoordAddress import CoordAddress
from voodoo.sessions.session_id import SessionId

from weblab.data.experiments import ExperimentId, ExperimentInstanceId

import weblab.core.coordinator.exc as CoordExc

import weblab.core.coordinator.sql.db as CoordinationDatabaseManager
import weblab.core.coordinator.sql.resource_manager as ResourcesManager
import weblab.core.coordinator.sql.reservations_manager as ReservationsManager
import weblab.core.coordinator.sql.post_reservation as PostReservationDataManager
import weblab.core.coordinator.confirmer as Confirmer
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.coordinator.status as coord_status

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



    ##########################################################################
    #
    #   Methods to retrieve the proper schedulers
    #
    @typecheck(Resource)
    def _get_scheduler_per_resource(self, resource):
        return self.schedulers[resource.resource_type]

    @typecheck(basestring)
    def _get_scheduler_aggregator_per_reservation(self, reservation_id):
        experiment_id = self.reservations_manager.get_experiment_id(reservation_id)
        return self._get_scheduler_aggregator(experiment_id)

    @typecheck(ExperimentId)
    def _get_scheduler_aggregator(self, experiment_id):
        experiment_id_str = experiment_id.to_weblab_str()
        aggregator = self.aggregators.get(experiment_id_str)
        if aggregator is None:
            raise CoordExc.ExperimentNotFoundError("Could not find scheduler aggregator associated to experiment id %s." % (experiment_id_str))
        return aggregator


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

    @logged()
    def list_experiments(self):
        return self.resources_manager.list_experiments()

    @logged()
    def list_laboratories_addresses(self):
        return self.resources_manager.list_laboratories_addresses()

    @logged()
    def list_resource_types(self):
        return self.schedulers.keys()

    @typecheck(ExperimentId)
    @logged()
    def list_sessions(self, experiment_id):
        """ list_sessions( experiment_id ) -> { session_id : status } """

        reservation_ids = self.reservations_manager.list_sessions(experiment_id)

        result = {}
        for reservation_id in reservation_ids:
            try:
                aggregator = self._get_scheduler_aggregator_per_reservation(reservation_id)
                best_reservation_status = aggregator.get_reservation_status(reservation_id)
            except CoordExc.CoordinatorError:
                # The reservation_id may expire since we called list_sessions,
                # so if there is a coordinator exception we just skip this
                # reservation_id
                continue
            result[reservation_id] = best_reservation_status
        return result

    @typecheck(ExperimentInstanceId, ITERATION(basestring))
    @logged()
    def mark_experiment_as_broken(self, experiment_instance_id, messages):
        resource_instance = self.resources_manager.get_resource_instance_by_experiment_instance_id(experiment_instance_id)
        return self.mark_resource_as_broken(resource_instance, messages)

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

    @typecheck(basestring, Resource, ITERATION(basestring))
    def _notify_experiment_status(self, new_status, resource_instance, messages = []):
        experiment_instance_ids = self.resources_manager.list_experiment_instance_ids_by_resource(resource_instance)
        if new_status == 'fixed':
            what = 'work again'
        else:
            what = 'not work'
        body = """The resource %s has changed its status to: %s\n\nTherefore the following experiment instances will %s:\n\n""" % (
                resource_instance, new_status, what)

        for experiment_instance_id in experiment_instance_ids:
            body += ("\t%s\n" % experiment_instance_id.to_weblab_str())

        if len(messages) > 0:
            body += "\nReasons: %r\n\nThe WebLab-Deusto system\n<%s>" % (messages, self.core_server_url)
        recipients = self._retrieve_recipients(experiment_instance_ids)
        subject = "[WebLab] Experiment %s: %s" % (resource_instance, new_status)

        if len(recipients) > 0:
            self.notifier.notify( recipients = recipients, body = body, subject = subject)


    ##########################################################################
    #
    # Perform a new reservation
    #
    @typecheck(ExperimentId, (float, int), int, bool, (dict, basestring), dict, dict)
    @logged()
    def reserve_experiment(self, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info, consumer_data):
        """
        priority: the less, the more priority
        """
        reservation_id = self.reservations_manager.create(experiment_id, client_initial_data, json.dumps(request_info), self.time_provider.get_datetime)
        aggregator = self._get_scheduler_aggregator(experiment_id)
        return aggregator.reserve_experiment(reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info), reservation_id

    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @typecheck(basestring)
    @logged()
    def get_reservation_status(self, reservation_id):
        # Just in case it was stored with the route
        reservation_id_without_route = reservation_id.split(';')[0]
        try:
            aggregator = self._get_scheduler_aggregator_per_reservation(reservation_id_without_route)
            return aggregator.get_reservation_status(reservation_id_without_route)

        except CoordExc.ExpiredSessionError:
            reservation_status = self.post_reservation_data_manager.find(reservation_id_without_route)
            if reservation_status is not None:
                return reservation_status
            raise
        except:
            import traceback
            traceback.print_exc()
            raise


    def is_post_reservation(self, reservation_id):
        return self.post_reservation_data_manager.find(reservation_id) is not None

    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @typecheck(CoordAddress, ExperimentId, basestring, basestring, SessionId, (basestring, type(None)), datetime.datetime, datetime.datetime)
    @logged()
    def confirm_experiment(self, experiment_coordaddress, experiment_id, reservation_id, lab_coordaddress_str, lab_session_id, server_initialization_response, initial_time, end_time):
        default_still_initialing      = False
        default_batch                 = False
        default_initial_configuration = "{}"
        if server_initialization_response is None or server_initialization_response == 'ok' or server_initialization_response == '':
            still_initializing = default_still_initialing
            batch = default_batch
            initial_configuration = default_initial_configuration
        else:
            try:
                response = json.loads(server_initialization_response)
                still_initializing    = response.get('keep_initializing', default_still_initialing)
                batch                 = response.get('batch', default_batch)
                initial_configuration = response.get('initial_configuration', default_initial_configuration)
            except Exception as e:
                log.log( Coordinator, log.level.Error, "Could not parse experiment server response: %s; %s; using default values" % (e, server_initialization_response) )
                log.log_exc( Coordinator, log.level.Warning )
                still_initializing    = default_still_initialing
                batch                 = default_batch
                initial_configuration = default_initial_configuration

        serialized_request_info, serialized_client_initial_data = self.reservations_manager.get_request_info_and_client_initial_data(reservation_id)
        request_info  = json.loads(serialized_request_info)

        # Put the entry into a queue that is continuosly storing information into the db
        initial_information_entry = TemporalInformationStore.InitialInformationEntry(
            reservation_id, experiment_id, experiment_coordaddress,
            initial_configuration, initial_time, end_time, request_info,
            serialized_client_initial_data )

        self.initial_store.put(initial_information_entry)

        now = self.time_provider.get_datetime()
        self.post_reservation_data_manager.create(reservation_id, now, now + self.expiration_delta, json.dumps(initial_configuration))

        if still_initializing:
            # TODO XXX
            raise NotImplementedError("Not yet implemented: still_initializing")

        aggregator = self._get_scheduler_aggregator_per_reservation(reservation_id)
        aggregator.confirm_experiment(reservation_id, lab_session_id, initial_configuration)

        if batch: # It has already finished, so make this experiment available to others
            self.finish_reservation(reservation_id)
            return

        self.confirmer.enqueue_should_finish(lab_coordaddress_str, lab_session_id, reservation_id)

    ################################################################
    #
    # Called when the experiment returns information about if the
    # session should end or not.
    #
    @typecheck(basestring, SessionId, basestring, (int, float))
    @logged()
    def confirm_should_finish(self, lab_coordaddress_str, lab_session_id, reservation_id, experiment_response):
        # If not reserved, don't try again
        try:
            current_status = self.get_reservation_status(reservation_id)
            if not isinstance(current_status, (coord_status.LocalReservedStatus, coord_status.RemoteReservedStatus)):
                return
        except CoordExc.CoordinatorError:
            return

        # 0: don't ask again
        if experiment_response == 0:
            return

        # -1: experiment finished
        if experiment_response < 0:
            self.finish_reservation(reservation_id)
            return

        # > 0: wait this time and ask again
        time.sleep(experiment_response)

        self.confirmer.enqueue_should_finish(lab_coordaddress_str, lab_session_id, reservation_id)


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

    @logged()
    def stop(self):
        for scheduler in self.schedulers.values():
            scheduler.stop()

    def _clean(self):
        for scheduler in self.schedulers.values():
            scheduler._clean()

        self.reservations_manager._clean()
        self.resources_manager._clean()
        self.post_reservation_data_manager._clean()

