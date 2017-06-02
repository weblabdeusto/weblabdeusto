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

import sys
import json
import time
import datetime
import random

from voodoo.log import logged
import voodoo.log as log

from sqlalchemy import not_
from sqlalchemy.orm import join
from sqlalchemy.orm.exc import StaleDataError, ConcurrentModificationError
from sqlalchemy.exc import IntegrityError, OperationalError

from voodoo.gen import CoordAddress
import voodoo.sessions.session_id as SessionId
from voodoo.override import Override

from weblab.core.coordinator.scheduler_transactions_synchronizer import SchedulerTransactionsSynchronizer
from weblab.core.coordinator.scheduler import Scheduler
from weblab.core.coordinator.sql.model import ResourceType, ResourceInstance, CurrentResourceSlot
from weblab.core.coordinator.sql.priority_queue_scheduler_model import ConcreteCurrentReservation, WaitingReservation
import weblab.core.coordinator.status as WSS

from weblab.data.experiments import ExperimentInstanceId

EXPIRATION_TIME  = 6 * 3600 # seconds

DEBUG = False

###########################################################
#
# TODO write some documentation
#

def exc_checker(func):
    def wrapper(*args, **kwargs):
        try:
            for _ in xrange(10):
                try:
                    return func(*args, **kwargs)
                except OperationalError as oe:
                    # XXX MySQL dependent!!!
                    if oe.orig.args[0] == 1213:
                        log.log(
                            PriorityQueueScheduler, log.level.Error,
                            "Deadlock found, restarting...%s" % func.__name__ )
                        log.log_exc(PriorityQueueScheduler, log.level.Warning)
                        continue
                    else:
                        raise
        except:
            if DEBUG:
                print("Error in exc_checker: ", sys.exc_info())
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
    def removing_current_resource_slot(self, session, resource_instance_id):
        resource_type = session.query(ResourceType).filter_by(name = resource_instance_id.resource_type).one()
        resource_instance = session.query(ResourceInstance).filter_by(name = resource_instance_id.resource_instance, resource_type = resource_type).one()

        current_resource_slot = resource_instance.slot

        if current_resource_slot is not None:
            slot_reservation = current_resource_slot.slot_reservation
            if slot_reservation is not None:
                concrete_current_reservations = current_resource_slot.slot_reservation.pq_current_reservations
                if len(concrete_current_reservations) > 0:
                    concrete_current_reservation = concrete_current_reservations[0]
                    waiting_reservation = WaitingReservation(resource_instance.resource_type, concrete_current_reservation.current_reservation_id, concrete_current_reservation.time, -1, concrete_current_reservation.initialization_in_accounting) # -1 : Highest priority
                    self.reservations_manager.downgrade_confirmation(session, concrete_current_reservation.current_reservation_id)
                    self.resources_manager.release_resource(session, current_resource_slot.slot_reservation)
                    session.add(waiting_reservation)
                    session.delete(concrete_current_reservation)
                    return True
        return False

    @exc_checker
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info):
        """
        priority: the less, the more priority
        """
        session = self.session_maker()
        try:
            resource_type = session.query(ResourceType).filter_by(name = self.resource_type_name).one()
            waiting_reservation = WaitingReservation(resource_type, reservation_id, time, priority, initialization_in_accounting)
            session.add(waiting_reservation)

            session.commit()
        finally:
            session.close()
        
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

        try:
            session = self.session_maker()
            try:
                self.reservations_manager.update(session, reservation_id)
                session.commit()
            finally:
                session.close()
        except StaleDataError:
            time.sleep(TIME_ANTI_RACE_CONDITIONS * random.random())
            return self.get_reservation_status(reservation_id)

        self._synchronizer.request_and_wait()

        reservation_id_with_route = '%s;%s.%s' % (reservation_id, reservation_id, self.core_server_route)

        return_current_status = False
        session = self.session_maker()
        try:
            #
            # If the current user is actually in a reservation assigned to a
            # certain laboratory, it may be in a Reserved state or in a
            # WaitingConfirmation state (meaning that it is still waiting for
            # a response from the Laboratory).
            #
            concrete_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == reservation_id).first()
            if concrete_current_reservation is not None:
                resource_instance     = concrete_current_reservation.slot_reservation.current_resource_slot.resource_instance
                requested_experiment_instance = None
                for experiment_instance in resource_instance.experiment_instances:
                    if experiment_instance.experiment_type == concrete_current_reservation.current_reservation.reservation.experiment_type:
                        requested_experiment_instance = experiment_instance
                        break
                if requested_experiment_instance is None:
                    raise Exception("Invalid state: there is an resource_instance of the resource_type the user was waiting for which doesn't have any experiment_instance of the experiment_type the user was waiting for")

                str_lab_coord_address        = requested_experiment_instance.laboratory_coord_address
                lab_coord_address            = CoordAddress.translate(str_lab_coord_address)
                obtained_time                = concrete_current_reservation.time
                lab_session_id               = concrete_current_reservation.lab_session_id
                if concrete_current_reservation.exp_info:
                    exp_info                 = json.loads(concrete_current_reservation.exp_info)
                else:
                    exp_info                 = {}
                initial_configuration        = concrete_current_reservation.initial_configuration
                initialization_in_accounting = concrete_current_reservation.initialization_in_accounting

                if concrete_current_reservation.timestamp_before is None:
                    timestamp_before  = None
                else:
                    timestamp_before  = datetime.datetime.fromtimestamp(concrete_current_reservation.timestamp_before)

                if concrete_current_reservation.timestamp_after is None:
                    timestamp_after   = None
                else:
                    timestamp_after   = datetime.datetime.fromtimestamp(concrete_current_reservation.timestamp_after)

                if lab_session_id is None:
                    return WSS.WaitingConfirmationQueueStatus(reservation_id_with_route, self.core_server_url)
                else:
                    if initialization_in_accounting:
                        before = concrete_current_reservation.timestamp_before
                    else:
                        before = concrete_current_reservation.timestamp_after

                    if before is not None:
                        remaining = (before + obtained_time) - self.time_provider.get_time()
                    else:
                        remaining = obtained_time

                    return WSS.LocalReservedStatus(reservation_id_with_route, lab_coord_address, SessionId.SessionId(lab_session_id), exp_info, obtained_time, initial_configuration, timestamp_before, timestamp_after, initialization_in_accounting, remaining, self.core_server_url)

            resource_type = session.query(ResourceType).filter_by(name = self.resource_type_name).one()
            waiting_reservation = session.query(WaitingReservation).filter_by(reservation_id = reservation_id, resource_type_id = resource_type.id).first()

            if waiting_reservation is None:
                waiting_reservations = []
            else:
                
                #
                # If it has not been assigned to any laboratory, then it might
                # be waiting in the queue of that resource type (Waiting) or
                # waiting for instances (WaitingInstances, meaning that there is
                # no resource of that type implemented)
                #
                waiting_reservations = session.query(WaitingReservation)\
                        .filter(WaitingReservation.resource_type == waiting_reservation.resource_type).order_by(WaitingReservation.priority, WaitingReservation.id).all()

            if waiting_reservation is None or waiting_reservation not in waiting_reservations:
                #
                # The position has changed and it is not in the list anymore!
                # This has happened using WebLab Bot with 65 users.
                #
                return_current_status = True

            else:
                position      = waiting_reservations.index(waiting_reservation)
                remaining_working_instances = False
                for resource_instance in waiting_reservation.resource_type.instances:
                    if resource_instance.slot is not None:
                        remaining_working_instances = True
                        break
        finally:
            session.close()

        if return_current_status:
            time.sleep(TIME_ANTI_RACE_CONDITIONS * random.random())
            return self.get_reservation_status(reservation_id)

        if remaining_working_instances:
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

        session = self.session_maker()
        try:
            if not self.reservations_manager.check(session, reservation_id):
                return

            possible_concrete_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == reservation_id).first()
            concrete_current_reservation = None
            if possible_concrete_current_reservation is not None:
                slot = possible_concrete_current_reservation.slot_reservation
                if slot is not None:
                    current_resource_slot = slot.current_resource_slot
                    if current_resource_slot is not None:
                        resource_instance = current_resource_slot.resource_instance
                        if resource_instance is not None:
                            resource_type = resource_instance.resource_type
                            if resource_type is not None and resource_type.name == self.resource_type_name:
                                concrete_current_reservation = possible_concrete_current_reservation

            if concrete_current_reservation is None:
                return

            concrete_current_reservation.lab_session_id        = lab_session_id.id
            concrete_current_reservation.initial_configuration = initial_configuration
            concrete_current_reservation.exp_info              = json.dumps(exp_info)
            concrete_current_reservation.set_timestamp_after(self.time_provider.get_time())

            session.commit()
        finally:
            session.close()


    ################################################################
    #
    # Called when the user disconnects or finishes the resource.
    #
    @exc_checker
    @logged()
    @Override(Scheduler)
    def finish_reservation(self, reservation_id):
        self._remove_expired_reservations()

        session = self.session_maker()
        try:
            possible_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == reservation_id).first()

            # Clean current reservation... if the current reservation is assigned to this scheduler
            concrete_current_reservation = None
            enqueue_free_experiment_args = None
            if possible_current_reservation is not None:
                slot = possible_current_reservation.slot_reservation
                if slot is not None:
                    current_resource_slot = slot.current_resource_slot
                    if current_resource_slot is not None:
                        resource_instance = current_resource_slot.resource_instance
                        if resource_instance is not None:
                            resource_type = resource_instance.resource_type
                            if resource_type is not None and resource_type.name == self.resource_type_name:
                                concrete_current_reservation = possible_current_reservation
                                enqueue_free_experiment_args = self._clean_current_reservation(session, concrete_current_reservation)

            db_resource_type = session.query(ResourceType).filter_by(name = self.resource_type_name).first()
            reservation_to_delete = concrete_current_reservation or session.query(WaitingReservation).filter_by(reservation_id = reservation_id, resource_type = db_resource_type).first()
            if reservation_to_delete is not None:
                session.delete(reservation_to_delete)

            session.commit()
            if enqueue_free_experiment_args is not None:
                self.confirmer.enqueue_free_experiment(*enqueue_free_experiment_args)
        finally:
            session.close()


    def _clean_current_reservation(self, session, concrete_current_reservation):
        enqueue_free_experiment_args = None
        if concrete_current_reservation is not None:
            resource_instance = concrete_current_reservation.slot_reservation.current_resource_slot.resource_instance
            if resource_instance is not None: # If the resource instance does not exist anymore, there is no need to call the free_experiment method
                lab_session_id     = concrete_current_reservation.lab_session_id
                experiment_instance = None
                for experiment_instance in resource_instance.experiment_instances:
                    if experiment_instance.experiment_type == concrete_current_reservation.current_reservation.reservation.experiment_type:
                        experiment_instance = experiment_instance
                        break

                if experiment_instance is not None: # If the experiment instance doesn't exist, there is no need to call the free_experiment method
                    lab_coord_address  = experiment_instance.laboratory_coord_address
                    reservation_id = concrete_current_reservation.current_reservation_id
                    enqueue_free_experiment_args = (lab_coord_address, reservation_id, lab_session_id, experiment_instance.to_experiment_instance_id())
            self.reservations_manager.downgrade_confirmation(session, concrete_current_reservation.current_reservation_id)
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

        ###########################################################
        # While there are free instances and waiting reservations,
        # take the first waiting reservation and set it to current
        # reservation. Make this repeatedly because we want to
        # commit each change
        #
        while True:
            session = self.session_maker()
            try:
                resource_type = session.query(ResourceType).filter(ResourceType.name == self.resource_type_name).first()

                #
                # Retrieve the first waiting reservation. If there is no one that
                # we haven't tried already, return
                #
                first_waiting_reservations = session.query(WaitingReservation).filter(WaitingReservation.resource_type == resource_type).order_by(WaitingReservation.priority, WaitingReservation.id)[:len(previously_waiting_reservation_ids) + 1]
                first_waiting_reservation = None
                for waiting_reservation in first_waiting_reservations:
                    if waiting_reservation.id not in previously_waiting_reservation_ids:
                        first_waiting_reservation = waiting_reservation
                        break

                if first_waiting_reservation is None:
                    return # There is no waiting reservation for this resource that we haven't already tried

                previously_waiting_reservation_ids.append(first_waiting_reservation.id)

                #
                # For the current resource_type, let's ask for
                # all the resource instances available (i.e. those
                # who have no SchedulingSchemaIndependentSlotReservation
                # associated)
                #
                free_instances = session.query(CurrentResourceSlot)\
                        .select_from(join(CurrentResourceSlot, ResourceInstance))\
                        .filter(not_(CurrentResourceSlot.slot_reservations.any()))\
                        .filter(ResourceInstance.resource_type == resource_type)\
                        .order_by(CurrentResourceSlot.id).all()

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
                    randomized_free_instances = free_instances

                for free_instance in randomized_free_instances:

                    resource_type = free_instance.resource_instance.resource_type
                    if resource_type is None:
                        continue # If suddenly the free_instance is not a free_instance anymore, try with other free_instance

                    #
                    # IMPORTANT: from here on every "continue" should first revoke the
                    # reservations_manager and resources_manager confirmations
                    #

                    self.reservations_manager.confirm(session, first_waiting_reservation.reservation_id)
                    slot_reservation = self.resources_manager.acquire_resource(session, free_instance)
                    total_time = first_waiting_reservation.time
                    initialization_in_accounting = first_waiting_reservation.initialization_in_accounting
                    start_time = self.time_provider.get_time()
                    concrete_current_reservation = ConcreteCurrentReservation(slot_reservation, first_waiting_reservation.reservation_id,
                                                        total_time, start_time, first_waiting_reservation.priority, first_waiting_reservation.initialization_in_accounting)
                    concrete_current_reservation.set_timestamp_before(self.time_provider.get_time())

                    client_initial_data = first_waiting_reservation.reservation.client_initial_data
                    request_info = json.loads(first_waiting_reservation.reservation.request_info)
                    username     = request_info.get('username')
                    username_unique = request_info.get('username_unique')
                    locale       = request_info.get('locale')

                    reservation_id = first_waiting_reservation.reservation_id
                    if reservation_id is None:
                        break # If suddenly the waiting_reservation is not a waiting_reservation anymore, so reservation is None, go again to the while True.

                    requested_experiment_type = first_waiting_reservation.reservation.experiment_type
                    selected_experiment_instance = None
                    for experiment_instance in free_instance.resource_instance.experiment_instances:
                        if experiment_instance.experiment_type == requested_experiment_type:
                            selected_experiment_instance = experiment_instance

                    if selected_experiment_instance is None:
                        # This resource is not valid for this user, other free_instance should be
                        # selected. Try with other, but first clean the acquired resources
                        self.reservations_manager.downgrade_confirmation(session, first_waiting_reservation.reservation_id)
                        self.resources_manager.release_resource(session, slot_reservation)
                        continue

                    experiment_instance_id = ExperimentInstanceId(selected_experiment_instance.experiment_instance_id, requested_experiment_type.exp_name, requested_experiment_type.cat_name)

                    laboratory_coord_address = selected_experiment_instance.laboratory_coord_address
                    try:
                        session.delete(first_waiting_reservation)
                        session.add(concrete_current_reservation)
                        session.commit()
                    except IntegrityError as ie:
                        if DEBUG:
                            print("IntegrityError when adding concrete_current_reservation: ", sys.exc_info())
                        # Other scheduler confirmed the user or booked the reservation, rollback and try again
                        # But log just in case
                        log.log(
                            PriorityQueueScheduler, log.level.Warning,
                            "IntegrityError looping on update_queues: %s" % ie )
                        log.log_exc(PriorityQueueScheduler, log.level.Info)
                        session.rollback()
                        break
                    except Exception as e:
                        if DEBUG:
                            print("Other error when adding concrete_current_reservation: ", sys.exc_info())

                        log.log(
                            PriorityQueueScheduler, log.level.Warning,
                            "Exception looping on update_queues: %s" % e )
                        log.log_exc(PriorityQueueScheduler, log.level.Info)
                        session.rollback()
                        break
                    else:
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
                                'request.experiment_id.experiment_name'            : experiment_instance_id.exp_name,
                                'request.experiment_id.category_name'              : experiment_instance_id.cat_name,
                                'request.username'                                 : username,
                                'request.username.unique'                          : username_unique,
                                'request.full_name'                                : username,
                                'request.locale'                                   : locale,
                            }
                        server_initial_data = json.dumps(deserialized_server_initial_data)
                        # server_initial_data will contain information such as "what was the last experiment used?".
                        # If a single resource was used by a binary experiment, then the next time may not require reprogramming the device
                        self.confirmer.enqueue_confirmation(laboratory_coord_address, reservation_id, experiment_instance_id, client_initial_data, server_initial_data, self.resource_type_name)
                        #
                        # After it, keep in the while True in order to add the next
                        # reservation
                        #
                        break
            except (ConcurrentModificationError, IntegrityError) as ie:
                # Something happened somewhere else, such as the user being confirmed twice, the experiment being reserved twice or so on.
                # Rollback and start again
                if DEBUG:
                    print("Other ConcurrentModificationError or IntegrityError in update_queues: ", sys.exc_info())

                log.log(
                    PriorityQueueScheduler, log.level.Warning,
                    "Exception while updating queues, reverting and trying again: %s" % ie )
                log.log_exc(PriorityQueueScheduler, log.level.Info)
                session.rollback()
            finally:
                session.close()


    ################################################
    #
    # Remove all reservations whose session has expired
    #
    def _remove_expired_reservations(self):
        session = self.session_maker()
        try:
            now = self.time_provider.get_time()
            current_expiration_time = datetime.datetime.utcfromtimestamp(now - EXPIRATION_TIME)

            reservations_removed = False
            enqueue_free_experiment_args_retrieved = []
            expired_query = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.expired_timestamp != 0).filter(ConcreteCurrentReservation.expired_timestamp < self.time_provider.get_time())

            for expired_concrete_current_reservation in expired_query.all():
                expired_reservation = expired_concrete_current_reservation.current_reservation_id
                if expired_reservation is None:
                    continue # Maybe it's not an expired_reservation anymore
                enqueue_free_experiment_args = self._clean_current_reservation(session, expired_concrete_current_reservation)
                enqueue_free_experiment_args_retrieved.append(enqueue_free_experiment_args)
                session.delete(expired_concrete_current_reservation)
                self.reservations_manager.delete(session, expired_reservation)
                reservations_removed = True

            for expired_reservation_id in self.reservations_manager.list_expired_reservations(session, current_expiration_time):
                concrete_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == expired_reservation_id).first()
                if concrete_current_reservation is not None:
                    enqueue_free_experiment_args = self._clean_current_reservation(session, concrete_current_reservation)
                    enqueue_free_experiment_args_retrieved.append(enqueue_free_experiment_args)
                    session.delete(concrete_current_reservation)
                waiting_reservation = session.query(WaitingReservation).filter(WaitingReservation.reservation_id == expired_reservation_id).first()
                if waiting_reservation is not None:
                    session.delete(waiting_reservation)

                self.reservations_manager.delete(session, expired_reservation_id)
                reservations_removed = True

            if reservations_removed:
                try:
                    session.commit()
                except ConcurrentModificationError as e:
                    if DEBUG:
                        print("Other error when commiting when reservations_removed: ", sys.exc_info())

                    log.log(
                        PriorityQueueScheduler, log.level.Warning,
                        "IntegrityError: %s" % e )
                    log.log_exc(PriorityQueueScheduler, log.level.Info)
                    pass # Someone else removed these users before us.
                else:
                    for enqueue_free_experiment_args in enqueue_free_experiment_args_retrieved:
                        if enqueue_free_experiment_args is not None:
                            self.confirmer.enqueue_free_experiment(*enqueue_free_experiment_args)
            else:
                session.rollback()
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
            for waiting_reservation in session.query(WaitingReservation).all():
                session.delete(waiting_reservation)
            for concrete_current_reservation in session.query(ConcreteCurrentReservation).all():
                session.delete(concrete_current_reservation)
            for current_resource_slot in session.query(CurrentResourceSlot).all():
                session.delete(current_resource_slot)

            session.commit()
        except ConcurrentModificationError:
            if DEBUG:
                print("Error when cleaning: ", sys.exc_info())

            pass # Another process is cleaning concurrently
        finally:
            session.close()


