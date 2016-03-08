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

import time
import datetime
import random
import json

from voodoo.log import logged
import voodoo.log as log
from voodoo.typechecker import typecheck

from voodoo.gen import CoordAddress
import voodoo.sessions.session_id as SessionId
from voodoo.override import Override

from weblab.core.coordinator.exc import ExpiredSessionError
from weblab.core.coordinator.scheduler_transactions_synchronizer import SchedulerTransactionsSynchronizer
from weblab.core.coordinator.scheduler import Scheduler
import weblab.core.coordinator.status as WSS

from weblab.core.coordinator.resource import Resource

from weblab.data.experiments import ExperimentInstanceId, ExperimentId

from weblab.core.coordinator.redis.constants import (
    WEBLAB_RESOURCE_RESERVATION_PQUEUE,
    WEBLAB_RESOURCE_SLOTS,
    WEBLAB_RESOURCE_RESERVATIONS,
    WEBLAB_RESOURCE_PQUEUE_RESERVATIONS,
    WEBLAB_RESOURCE_PQUEUE_POSITIONS,
    WEBLAB_RESOURCE_PQUEUE_MAP,
    WEBLAB_RESOURCE_PQUEUE_SORTED,
    WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS,

    LAB_COORD,
    CLIENT_INITIAL_DATA,
    REQUEST_INFO,
    EXPERIMENT_TYPE,
    EXPERIMENT_INSTANCE,
    START_TIME,
    TIME,
    INITIALIZATION_IN_ACCOUNTING,
    PRIORITY,
    TIMESTAMP_BEFORE,
    TIMESTAMP_AFTER,
    LAB_SESSION_ID,
    EXP_INFO,
    INITIAL_CONFIGURATION,
    RESOURCE_INSTANCE,
    ACTIVE_STATUS,
    STATUS_RESERVED,
    STATUS_WAITING_CONFIRMATION,
)

EXPIRATION_TIME  = 6 * 3600 # seconds

DEBUG = False

###########################################################
#
# TODO write some documentation
#

def exc_checker(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            if DEBUG:
                import traceback
                traceback.print_exc()
            log.log(
                PriorityQueueScheduler, log.level.Error,
                "Unexpected exception while running %s" % func.__name__ )
            log.log_exc(PriorityQueueScheduler, log.level.Warning)
            raise
	wrapper.__name__ = func.__name__
	wrapper.__doc__ = func.__doc__
    return wrapper
	
TIME_ANTI_RACE_CONDITIONS = 0.1

class PriorityQueueScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, randomize_instances = True, **kwargs):
        super(PriorityQueueScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

        self.randomize_instances = randomize_instances

        self._synchronizer = SchedulerTransactionsSynchronizer(self)
        self._synchronizer.start()

    @Override(Scheduler)
    def stop(self):
        self._synchronizer.stop()

    @Override(Scheduler)
    def is_remote(self):
        return False

    @exc_checker
    @logged()
    @Override(Scheduler)
    @typecheck(typecheck.ANY, typecheck.ANY, Resource)
    def removing_current_resource_slot(self, client, resource):
        weblab_resource_instance_reservations = WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS % (resource.resource_type, resource.resource_instance)

        current_reservation_ids = client.smembers(weblab_resource_instance_reservations)
        if len(current_reservation_ids) > 0:
            current_reservation_id = list(current_reservation_ids)[0]
            if client.srem(weblab_resource_instance_reservations, current_reservation_id):
                self.reservations_manager.downgrade_confirmation(current_reservation_id)
                self.resources_manager.release_resource(resource)
                # Remove data that was added when confirmed
                weblab_reservation_pqueue   = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, current_reservation_id)
                reservation_data_str = client.get(weblab_reservation_pqueue)
                reservation_data = json.loads(reservation_data_str)
                reservation_data.pop(ACTIVE_STATUS,    None)
                reservation_data.pop(TIMESTAMP_BEFORE, None)
                reservation_data.pop(TIMESTAMP_AFTER,  None)
                reservation_data.pop(LAB_SESSION_ID,   None)
                reservation_data.pop(EXP_INFO,         None)
                reservation_data_str = json.dumps(reservation_data)
                reservation_data = client.set(weblab_reservation_pqueue, reservation_data_str)
                # Add back to the queue

                weblab_resource_pqueue_map          = WEBLAB_RESOURCE_PQUEUE_MAP          % self.resource_type_name
                weblab_resource_pqueue_sorted       = WEBLAB_RESOURCE_PQUEUE_SORTED       % self.resource_type_name

                filled_reservation_id = client.hget(weblab_resource_pqueue_map, current_reservation_id)
                client.zadd(weblab_resource_pqueue_sorted, filled_reservation_id, -1)
                return True
           
        return False

    @exc_checker
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info):
        """
        priority: the less, the more priority
        """
        client = self.redis_maker()

        # For indexing purposes
        weblab_reservation_pqueue           = WEBLAB_RESOURCE_RESERVATION_PQUEUE  % (self.resource_type_name, reservation_id)
        weblab_resource_reservations        = WEBLAB_RESOURCE_RESERVATIONS        % self.resource_type_name

        # Queue management
        weblab_resource_pqueue_reservations = WEBLAB_RESOURCE_PQUEUE_RESERVATIONS % self.resource_type_name
        weblab_resource_pqueue_positions    = WEBLAB_RESOURCE_PQUEUE_POSITIONS    % self.resource_type_name
        weblab_resource_pqueue_map          = WEBLAB_RESOURCE_PQUEUE_MAP          % self.resource_type_name
        weblab_resource_pqueue_sorted       = WEBLAB_RESOURCE_PQUEUE_SORTED       % self.resource_type_name
   
        # Within the same priority, we want all to sort all the requests by the order they came.
        # In order to support this, we increase a long enough value and put it before the reservaiton_id
        current_position = client.incr(weblab_resource_pqueue_positions)
        filled_reservation_id = "%s_%s" % (str(current_position).zfill(100), reservation_id)

        pipeline = client.pipeline()

        pipeline.hset(weblab_resource_pqueue_map,          reservation_id,        filled_reservation_id)
        pipeline.zadd(weblab_resource_pqueue_sorted,       filled_reservation_id, priority)

        pipeline.sadd(weblab_resource_reservations,        reservation_id)
        pipeline.sadd(weblab_resource_pqueue_reservations, reservation_id)

        generic_data = { 
            TIME                         : time,
            INITIALIZATION_IN_ACCOUNTING : initialization_in_accounting,
            PRIORITY                     : priority,
        }
        pipeline.set(weblab_reservation_pqueue, json.dumps(generic_data))
        
        pipeline.execute()

        return self.get_reservation_status(reservation_id)



    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @exc_checker
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        self._remove_expired_reservations()

        expired = self.reservations_manager.update(reservation_id)
        if expired:
            self._delete_reservation(reservation_id)
            raise ExpiredSessionError("Expired reservation")
   
        self._synchronizer.request_and_wait()

        reservation_id_with_route = '%s;%s.%s' % (reservation_id, reservation_id, self.core_server_route)

        client = self.redis_maker()

        weblab_reservation_pqueue = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id)
        reservation_data_str = client.get(weblab_reservation_pqueue)
        if reservation_data_str is None:
            log.log(
                PriorityQueueScheduler, log.level.Error,
                "get_reservation_status called with a reservation_id that is not registered (not found on weblab_reservation_pqueue). Returning a WaitingInstanceStatus")
            return WSS.WaitingInstancesQueueStatus(reservation_id_with_route, 50)

        reservation_data = json.loads(reservation_data_str)

        if ACTIVE_STATUS in reservation_data:
            # Reserved or Waiting reservation
            status = reservation_data[ACTIVE_STATUS]
            
            # It may be just waiting for the experiment server to respond
            if status == STATUS_WAITING_CONFIRMATION:
                return WSS.WaitingConfirmationQueueStatus(reservation_id_with_route, self.core_server_url)

            # Or the experiment server already responded and therefore we have all this data
            str_lab_coord_address        = reservation_data[LAB_COORD]
            obtained_time                = reservation_data[TIME]
            initialization_in_accounting = reservation_data[INITIALIZATION_IN_ACCOUNTING]
            lab_session_id               = reservation_data[LAB_SESSION_ID]  
            initial_configuration        = reservation_data[INITIAL_CONFIGURATION]
            timestamp_before_tstamp      = reservation_data[TIMESTAMP_BEFORE]
            timestamp_after_tstamp       = reservation_data[TIMESTAMP_AFTER]
            if EXP_INFO in reservation_data and reservation_data[EXP_INFO]:
                exp_info                 = json.loads(reservation_data[EXP_INFO])
            else:
                exp_info                 = {}
            timestamp_before             = datetime.datetime.fromtimestamp(timestamp_before_tstamp)
            timestamp_after              = datetime.datetime.fromtimestamp(timestamp_after_tstamp)
            lab_coord_address            = CoordAddress.translate(str_lab_coord_address)

            if initialization_in_accounting:
                before = timestamp_before_tstamp
            else:
                before = timestamp_after_tstamp

            if before is not None:
                remaining = (before + obtained_time) - self.time_provider.get_time()
            else:
                remaining = obtained_time
            
            return WSS.LocalReservedStatus(reservation_id_with_route, lab_coord_address, SessionId.SessionId(lab_session_id), exp_info, obtained_time, initial_configuration, timestamp_before, timestamp_after, initialization_in_accounting, remaining, self.core_server_url)

        # else it's waiting

        weblab_resource_pqueue_map          = WEBLAB_RESOURCE_PQUEUE_MAP    % self.resource_type_name
        weblab_resource_pqueue_sorted       = WEBLAB_RESOURCE_PQUEUE_SORTED % self.resource_type_name

        filled_reservation_id = client.hget(weblab_resource_pqueue_map, reservation_id)
        if filled_reservation_id is None:
            log.log(
                PriorityQueueScheduler, log.level.Error,
                "get_reservation_status called with a reservation_id that is not registered (not found on the reservations map). Returning a WaitingInstanceStatus")
            return WSS.WaitingInstancesQueueStatus(reservation_id_with_route, 50)

        position = client.zrank(weblab_resource_pqueue_sorted, filled_reservation_id)

        if position is None: # It's not in the queue now
            time.sleep(TIME_ANTI_RACE_CONDITIONS * random.random())
            return self.get_reservation_status(reservation_id)

        if self.resources_manager.are_resource_instances_working(self.resource_type_name):
            return WSS.WaitingQueueStatus(reservation_id_with_route, position)
        else:
            return WSS.WaitingInstancesQueueStatus(reservation_id_with_route, position)


    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @exc_checker
    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration, exp_info):
        self._remove_expired_reservations()

        weblab_reservation_pqueue = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id)

        client = self.redis_maker()
        pqueue_reservation_data_str = client.get(weblab_reservation_pqueue)
        if pqueue_reservation_data_str is None:
            return

        pqueue_reservation_data = json.loads(pqueue_reservation_data_str)
        resource_instance_str = pqueue_reservation_data.get(RESOURCE_INSTANCE)
        if resource_instance_str is not None:
            resource_instance = Resource.parse(resource_instance_str)
            if not self.resources_manager.check_working(resource_instance):
                # TODO: if the experiment is broken and the student is ACTIVE_STATUS, something should be done
                # 
                return

        pqueue_reservation_data[LAB_SESSION_ID]        = lab_session_id.id
        pqueue_reservation_data[INITIAL_CONFIGURATION] = initial_configuration
        pqueue_reservation_data[TIMESTAMP_AFTER]       = self.time_provider.get_time()
        pqueue_reservation_data[ACTIVE_STATUS]         = STATUS_RESERVED
        pqueue_reservation_data[EXP_INFO]              = json.dumps(exp_info)

        pqueue_reservation_data_str = json.dumps(pqueue_reservation_data)
        client.set(weblab_reservation_pqueue, pqueue_reservation_data_str)

    ################################################################
    #
    # Called when the user disconnects or finishes the resource.
    #
    @exc_checker
    @logged()
    @Override(Scheduler)
    def finish_reservation(self, reservation_id):
        self._remove_expired_reservations()

        weblab_reservation_pqueue = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id)

        client = self.redis_maker()
        pqueue_reservation_data_str = client.get(weblab_reservation_pqueue)
        if pqueue_reservation_data_str is None:
            return

        pqueue_reservation_data = json.loads(pqueue_reservation_data_str)
        if ACTIVE_STATUS in pqueue_reservation_data:
            enqueue_free_experiment_args = self._clean_current_reservation(reservation_id)
        else:
            enqueue_free_experiment_args = None
            
        self._delete_reservation(reservation_id)

        if enqueue_free_experiment_args is not None:
            self.confirmer.enqueue_free_experiment(*enqueue_free_experiment_args)


    def _clean_current_reservation(self, reservation_id):
        client = self.redis_maker()

        enqueue_free_experiment_args = None
        if reservation_id is not None:
            weblab_reservation_pqueue = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id)
            reservation_data_str = client.get(weblab_reservation_pqueue)
            if reservation_data_str is not None:
                downgraded = self.reservations_manager.downgrade_confirmation(reservation_id)
                if downgraded:
                    reservation_data      = json.loads(reservation_data_str)
                    resource_instance_str = reservation_data.get(RESOURCE_INSTANCE)
                    if resource_instance_str is not None:
                        resource_instance       = Resource.parse(resource_instance_str)
                        weblab_resource_pqueue_instance_reservations = WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS % (resource_instance.resource_type, resource_instance.resource_instance)
                        client.srem(weblab_resource_pqueue_instance_reservations, reservation_id)
                        # print "RELEASING AT _clean_current_reservation. SHOULD NEVER HAPPEN."
                        # self.resources_manager.release_resource(resource_instance)
                        lab_session_id          = reservation_data.get(LAB_SESSION_ID)
                        experiment_instance_str = reservation_data.get(EXPERIMENT_INSTANCE)
                        experiment_instance_id  = ExperimentInstanceId.parse(experiment_instance_str)
                        if experiment_instance_id is not None: 
                            # If the experiment instance doesn't exist, there is no need to call the free_experiment method
                            lab_coord_address  = reservation_data.get(LAB_COORD)
                            enqueue_free_experiment_args = (lab_coord_address, reservation_id, lab_session_id, experiment_instance_id)
                # otherwise the student has been removed
        return enqueue_free_experiment_args

    def update(self):
        self._update_queues()

    #############################################################
    #
    # Take the queue of a given Resource Type and update it
    #
    @exc_checker
    def _update_queues(self):
        ###########################################################
        # There are reasons why a waiting reservation may not be
        # able to be promoted while the next one is. For instance,
        # if a user is waiting for "pld boards", but only for
        # instances of "pld boards" which have a "ud-binary@Binary
        # experiments" server running. If only a "ud-pld@PLD
        # Experiments" is available, then this user will not be
        # promoted and the another user which is waiting for a
        # "ud-pld@PLD Experiments" can be promoted.
        #
        # Therefore, we have a list of the IDs of the waiting
        # reservations we previously thought that they couldn't be
        # promoted in this iteration. They will have another
        # chance in the next run of _update_queues.
        #
        previously_waiting_reservation_ids = []

        weblab_resource_pqueue_map    = WEBLAB_RESOURCE_PQUEUE_MAP    % self.resource_type_name
        weblab_resource_pqueue_sorted = WEBLAB_RESOURCE_PQUEUE_SORTED % self.resource_type_name 
        weblab_resource_slots         = WEBLAB_RESOURCE_SLOTS         % self.resource_type_name 



        ###########################################################
        # While there are free instances and waiting reservations,
        # take the first waiting reservation and set it to current
        # reservation. Make this repeatedly because we want to
        # commit each change
        #
        while True:
            client = self.redis_maker()
            filled_waiting_reservation_ids = client.zrangebyscore(weblab_resource_pqueue_sorted, -10000, +10000, start=0, num=len(previously_waiting_reservation_ids) + 1)
            first_waiting_reservation_id = None
            for filled_waiting_reservation_id in filled_waiting_reservation_ids:
                waiting_reservation_id = filled_waiting_reservation_id[filled_waiting_reservation_id.find('_')+1:]
                if waiting_reservation_id not in previously_waiting_reservation_ids:
                    first_waiting_reservation_id = waiting_reservation_id
                    break

            if first_waiting_reservation_id is None:
                return # There is no waiting reservation for this resource that we haven't already tried

            previously_waiting_reservation_ids.append(first_waiting_reservation_id)

            #
            # For the current resource_type, let's ask for
            # all the resource instances available (i.e. those
            # who are a member on weblab:resource:%s:slots )
            #
            free_instances = [ Resource(self.resource_type_name, resource_instance) 
                                for resource_instance in client.smembers(weblab_resource_slots) ]

            if len(free_instances) == 0:
                # If there is no free instance, just return
                return

            #
            # Select the correct free_instance for the current student among
            # all the free_instances
            #
            if self.randomize_instances:
                randomized_free_instances = [ free_instance for free_instance in free_instances ]
                random.shuffle(randomized_free_instances)
            else:
                randomized_free_instances = sorted(free_instances, cmp=lambda r1, r2: cmp(r1.resource_type, r2.resource_type) or cmp(r1.resource_instance, r2.resource_instance))

            for free_instance in randomized_free_instances:
                #
                # IMPORTANT: from here on every "continue" should first revoke the
                # reservations_manager and resources_manager confirmations
                #

                working = self.resources_manager.check_working(free_instance)
                if not working:
                    # The instance is not working
                    continue

                confirmed = self.reservations_manager.confirm(first_waiting_reservation_id)
                if not confirmed:
                    # student has already been confirmed somewhere else, so don't try with other
                    # instances, but rather with other student
                    break

                acquired = self.resources_manager.acquire_resource(free_instance)
                # print "ACQUIRED", free_instance, acquired, time.time()
                if not acquired:
                    # the instance has been acquired by someone else. unconfirm student and
                    # try again with other free_instance
                    self.reservations_manager.downgrade_confirmation(first_waiting_reservation_id)
                    continue

                weblab_resource_pqueue_instance_reservations = WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS % (self.resource_type_name, free_instance.resource_instance)
                client.sadd(weblab_resource_pqueue_instance_reservations, first_waiting_reservation_id)


                weblab_reservation_pqueue  = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, first_waiting_reservation_id)
                pqueue_reservation_data_str = client.get(weblab_reservation_pqueue)
                reservation_data            = self.reservations_manager.get_reservation_data(first_waiting_reservation_id)
                if pqueue_reservation_data_str is None or reservation_data is None:
                    # the student is not here anymore; downgrading confirmation is not required
                    # but releasing the resource is; and skip the rest of the free instances
                    self.resources_manager.release_resource(free_instance)
                    client.srem(weblab_resource_pqueue_instance_reservations, first_waiting_reservation_id)
                    break

                pqueue_reservation_data = json.loads(pqueue_reservation_data_str)

                start_time                                 = self.time_provider.get_time()
                total_time                                 = pqueue_reservation_data[TIME]
                pqueue_reservation_data[START_TIME]        = start_time


                pqueue_reservation_data[TIMESTAMP_BEFORE]  = start_time
                pqueue_reservation_data[ACTIVE_STATUS]     = STATUS_WAITING_CONFIRMATION
                pqueue_reservation_data[RESOURCE_INSTANCE] = free_instance.to_weblab_str()
                initialization_in_accounting               = pqueue_reservation_data[INITIALIZATION_IN_ACCOUNTING]

                client_initial_data       = reservation_data[CLIENT_INITIAL_DATA]
                request_info              = json.loads(reservation_data[REQUEST_INFO])
                username                  = request_info.get('username')
                locale                    = request_info.get('locale')

                requested_experiment_type = ExperimentId.parse(reservation_data[EXPERIMENT_TYPE])

                selected_experiment_instance = None
                experiment_instances = self.resources_manager.list_experiment_instance_ids_by_resource(free_instance)
                for experiment_instance in experiment_instances:
                    if experiment_instance.to_experiment_id() == requested_experiment_type:
                        selected_experiment_instance = experiment_instance

                if selected_experiment_instance is None:
                    # This resource is not valid for this user, other free_instance should be
                    # selected. Try with other, but first clean the acquired resources
                    self.reservations_manager.downgrade_confirmation(first_waiting_reservation_id)
                    self.resources_manager.release_resource(free_instance)
                    client.srem(weblab_resource_pqueue_instance_reservations, first_waiting_reservation_id)
                    continue

                pqueue_reservation_data[EXPERIMENT_INSTANCE] = selected_experiment_instance.to_weblab_str()
                laboratory_coord_address = self.resources_manager.get_laboratory_coordaddress_by_experiment_instance_id(selected_experiment_instance)
                pqueue_reservation_data[LAB_COORD] = laboratory_coord_address
                client.set(weblab_reservation_pqueue, json.dumps(pqueue_reservation_data))

                filled_reservation_id = client.hget(weblab_resource_pqueue_map, first_waiting_reservation_id)
                client.zrem(weblab_resource_pqueue_sorted, filled_reservation_id)

                #
                # Enqueue the confirmation, since it might take a long time
                # (for instance, if the laboratory server does not reply because
                # of any network problem, or it just takes too much in replying),
                # so this method might take too long. That's why we enqueue these
                # petitions and run them in other threads.
                #
                deserialized_server_initial_data = {
                        'priority.queue.slot.length'                       : '%s' % total_time,
                        'priority.queue.slot.start'                        : '%s' % datetime.datetime.fromtimestamp(start_time),
                        'priority.queue.slot.initialization_in_accounting' : initialization_in_accounting,
                        'request.experiment_id.experiment_name'            : selected_experiment_instance.exp_name,
                        'request.experiment_id.category_name'              : selected_experiment_instance.cat_name,
                        'request.username'                                 : username,
                        'request.full_name'                                : username,
                        'request.locale'                                   : locale,
                        # TODO: add the username and user full name here
                    }
                server_initial_data = json.dumps(deserialized_server_initial_data)
                # server_initial_data will contain information such as "what was the last experiment used?".
                # If a single resource was used by a binary experiment, then the next time may not require reprogramming the device
                self.confirmer.enqueue_confirmation(laboratory_coord_address, first_waiting_reservation_id, selected_experiment_instance, client_initial_data, server_initial_data, self.resource_type_name)
                #
                # After it, keep in the while True in order to add the next
                # reservation
                #
                break

    ################################################
    #
    # Remove all reservations whose session has expired
    #
    @exc_checker
    def _remove_expired_reservations(self):
        now = self.time_provider.get_time()

        enqueue_free_experiment_args_retrieved = []

        client = self.redis_maker()
        weblab_resource_pqueue_reservations = WEBLAB_RESOURCE_PQUEUE_RESERVATIONS % self.resource_type_name 
        reservations = [ reservation_id for reservation_id in client.smembers(weblab_resource_pqueue_reservations) ]

        # Since there might be a lot of reservations, create a pipeline and retrieve 
        # every reservation data in a row
        pipeline = client.pipeline()
        for reservation_id in reservations:
            weblab_reservation_pqueue = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id)
            pipeline.get(weblab_reservation_pqueue)
        results = pipeline.execute()
       
        for reservation_id, reservation_data in zip(reservations, results):
            if reservation_data is not None:
                data = json.loads(reservation_data)
                if ACTIVE_STATUS in data:
                    total_time                   = data[TIME]
                    timestamp_before             = data[TIMESTAMP_BEFORE]
                    timestamp_after              = data.get(TIMESTAMP_AFTER)
                    initialization_in_accounting = data[INITIALIZATION_IN_ACCOUNTING]
                    # if timestamp_after is None and initialization should not be considered,
                    # then we can not calculate if the time has expired, so we skip it (it will
                    # be considered as expired for lack of LATEST_ACCESS
                    if timestamp_after is not None or initialization_in_accounting:
                        timestamp = timestamp_before if initialization_in_accounting else timestamp_after
                        if now >= timestamp + total_time: # Expired
                            enqueue_free_experiment_args = self._clean_current_reservation(reservation_id)
                            enqueue_free_experiment_args_retrieved.append(enqueue_free_experiment_args)
                            self._delete_reservation(reservation_id)
                            self.reservations_manager.delete(reservation_id)

        # Anybody with latest_access later than this point is expired
        current_expiration_time = datetime.datetime.utcfromtimestamp(now - EXPIRATION_TIME)

        for expired_reservation_id in self.reservations_manager.list_expired_reservations(current_expiration_time):
            weblab_reservation_pqueue = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, expired_reservation_id)
            pqueue_reservation_data_str = client.get(weblab_reservation_pqueue)
            if pqueue_reservation_data_str is None:
                continue

            pqueue_reservation_data = json.loads(pqueue_reservation_data_str)

            if ACTIVE_STATUS in pqueue_reservation_data:
                enqueue_free_experiment_args = self._clean_current_reservation(expired_reservation_id)
                enqueue_free_experiment_args_retrieved.append(enqueue_free_experiment_args)

            self._delete_reservation(expired_reservation_id)
            self.reservations_manager.delete(expired_reservation_id)

        for enqueue_free_experiment_args in enqueue_free_experiment_args_retrieved:
            if enqueue_free_experiment_args is not None:
                self.confirmer.enqueue_free_experiment(*enqueue_free_experiment_args)

    def _delete_reservation(self, reservation_id):
        weblab_resource_pqueue_reservations          = WEBLAB_RESOURCE_PQUEUE_RESERVATIONS % self.resource_type_name
        weblab_resource_pqueue_map                   = WEBLAB_RESOURCE_PQUEUE_MAP    % self.resource_type_name
        weblab_resource_pqueue_sorted                = WEBLAB_RESOURCE_PQUEUE_SORTED % self.resource_type_name
        weblab_reservation_pqueue                    = WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id)

        resource_instances = self.resources_manager.list_resource_instances_by_type(self.resource_type_name)

        client = self.redis_maker()
        pipeline = client.pipeline()

        for resource_instance in resource_instances:
            weblab_resource_pqueue_instance_reservations = WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS % (self.resource_type_name, resource_instance.resource_instance)
            pipeline.srem(weblab_resource_pqueue_instance_reservations, reservation_id)

        pipeline.srem(weblab_resource_pqueue_reservations, reservation_id)
        pipeline.delete(weblab_reservation_pqueue)
        pipeline.execute()

        filled_reservation_id = client.hget(weblab_resource_pqueue_map, reservation_id)
        client.hdel(weblab_resource_pqueue_map, reservation_id)
        client.zrem(weblab_resource_pqueue_sorted, filled_reservation_id)
        

    ##############################################################
    #
    # ONLY FOR TESTING: It completely removes the whole database
    #
    @Override(Scheduler)
    def _clean(self):
        client = self.redis_maker()

        for reservation_id in self.reservations_manager.list_all_reservations():
            client.delete(WEBLAB_RESOURCE_RESERVATION_PQUEUE % (self.resource_type_name, reservation_id))
            client.delete(WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS % (self.resource_type_name, '*'))

        for resource_instance in self.resources_manager.list_resource_instances_by_type(self.resource_type_name):
            client.delete(WEBLAB_RESOURCE_PQUEUE_INSTANCE_RESERVATIONS % (self.resource_type_name, resource_instance.resource_instance))
        client.delete(WEBLAB_RESOURCE_PQUEUE_RESERVATIONS % self.resource_type_name)
        client.delete(WEBLAB_RESOURCE_PQUEUE_POSITIONS    % self.resource_type_name)
        client.delete(WEBLAB_RESOURCE_PQUEUE_MAP          % self.resource_type_name)
        client.delete(WEBLAB_RESOURCE_PQUEUE_SORTED       % self.resource_type_name)

