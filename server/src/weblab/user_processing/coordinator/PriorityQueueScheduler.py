#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# 

import datetime

from voodoo.log import logged
import voodoo.LogLevel as LogLevel
import voodoo.log as log

import sqlalchemy
from sqlalchemy import not_
from sqlalchemy.orm import join
from sqlalchemy.exc import IntegrityError, OperationalError

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.sessions.SessionId as SessionId
from voodoo.override import Override

from weblab.user_processing.coordinator.Scheduler import Scheduler
from weblab.user_processing.coordinator.CoordinatorModel import ResourceType, ResourceInstance, CurrentResourceSlot
from weblab.user_processing.coordinator.PriorityQueueSchedulerModel import ConcreteCurrentReservation, WaitingReservation
import weblab.user_processing.coordinator.WebLabQueueStatus as WQS

from weblab.data.experiments.ExperimentInstanceId import ExperimentInstanceId

EXPIRATION_TIME  = 3600 # seconds

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
                except OperationalError, oe:
                    if oe.orig.args[0] == 1213:
                        log.log(
                            PriorityQueueScheduler, LogLevel.Error,
                            "Deadlock found, restarting...%s" % func.__name__ )
                        log.log_exc(PriorityQueueScheduler, LogLevel.Warning)
                        continue
                    else:
                        raise
        except:
            log.log(
                PriorityQueueScheduler, LogLevel.Error,
                "Unexpected exception while running %s" % func.__name__ )
            log.log_exc(PriorityQueueScheduler, LogLevel.Warning)
            raise
	wrapper.__name__ = func.__name__
	wrapper.__doc__ = func.__doc__
    return wrapper
	

class PriorityQueueScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, **kwargs):
        super(PriorityQueueScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

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
                    waiting_reservation = WaitingReservation(resource_instance.resource_type, concrete_current_reservation.current_reservation_id, concrete_current_reservation.time,
                            -1, concrete_current_reservation.client_initial_data ) # -1 : Highest priority
                    self.reservations_manager.downgrade_confirmation(session, concrete_current_reservation.current_reservation_id)
                    self.resources_manager.release_resource(session, current_resource_slot.slot_reservation)
                    session.add(waiting_reservation)
                    session.delete(concrete_current_reservation)
                    return True
        return False

    @exc_checker
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, client_initial_data):
        """
        priority: the less, the more priority
        """
        session = self.session_maker()
        try:
            resource_type = session.query(ResourceType).filter_by(name = self.resource_type_name).one()
            waiting_reservation = WaitingReservation(resource_type, reservation_id, time, priority, client_initial_data)
            session.add(waiting_reservation)

            session.commit()
        finally:
            session.close()

        return self.get_reservation_status(reservation_id), reservation_id



    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    @exc_checker
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        self._remove_expired_reservations()

        session = self.session_maker()
        try:
            self.reservations_manager.update(session, reservation_id)
            session.commit()
        finally:
            session.close()

        self._update_queues()

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

                str_lab_coord_address = requested_experiment_instance.laboratory_coord_address
                lab_coord_address     = CoordAddress.CoordAddress.translate_address(str_lab_coord_address)
                obtained_time         = concrete_current_reservation.time
                lab_session_id        = concrete_current_reservation.lab_session_id
                if lab_session_id is None:
                    return WQS.WaitingConfirmationQueueStatus(lab_coord_address, obtained_time)
                else:
                    return WQS.ReservedQueueStatus(lab_coord_address, SessionId.SessionId(lab_session_id), obtained_time)

            resource_type = session.query(ResourceType).filter_by(name = self.resource_type_name).one()
            waiting_reservation = session.query(WaitingReservation).filter_by(reservation_id = reservation_id, resource_type_id = resource_type.id).first()
          
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
            return self.get_reservation_status(reservation_id)

        if remaining_working_instances:
            return WQS.WaitingQueueStatus(position)
        else:
            return WQS.WaitingInstancesQueueStatus(position)


    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @exc_checker
    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id):
        self._remove_expired_reservations()

        session = self.session_maker()
        try:    
            if not self.reservations_manager.check(session, reservation_id):
                session.close()
                return

            concrete_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == reservation_id).first()
            if concrete_current_reservation is None:
                session.close()
                return

            concrete_current_reservation.lab_session_id = lab_session_id.id

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
            concrete_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == reservation_id).first()

            self._clean_current_reservation(session, concrete_current_reservation)
                
            reservation_to_delete = concrete_current_reservation or session.query(WaitingReservation).filter(WaitingReservation.reservation_id == reservation_id).first()
            if reservation_to_delete is not None:
                session.delete(reservation_to_delete) 

            session.commit() 
        finally:
            session.close()

    def _clean_current_reservation(self, session, concrete_current_reservation):
        if concrete_current_reservation is not None:
            resource_instance = concrete_current_reservation.slot_reservation.current_resource_slot.resource_instance
            if resource_instance is not None: # If the resource instance does not exist anymore, there is no need to call the free_experiment method
                lab_session_id     = concrete_current_reservation.lab_session_id
                experiment_instance = None
                for experiment_instance in resource_instance.experiment_instances:
                    if experiment_instance.experiment_type == concrete_current_reservation.current_reservation.reservation.experiment_type:
                        experiment_instance = experiment_instance
                        break

                if experiment_instance is not None and lab_session_id is not None: # If the experiment instance doesn't exist, there is no need to call the free_experiment method
                    lab_coord_address  = experiment_instance.laboratory_coord_address
                    self.confirmer.enqueue_free_experiment(lab_coord_address, lab_session_id)
            self.reservations_manager.downgrade_confirmation(session, concrete_current_reservation.current_reservation_id)
            self.resources_manager.release_resource(session, concrete_current_reservation.slot_reservation)

    #############################################################
    # 
    # Take the queue of a given Resource Type and update it
    # 
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
                # who have no ConcreteCurrentReservation associated)
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
                for free_instance in free_instances:

                    resource_type = free_instance.resource_instance.resource_type
                    if resource_type is None:
                        continue # If suddenly the free_instance is not a free_instance anymore, try with other free_instance

                    # 
                    # IMPORTANT: from here on every "continue" should first revoke the 
                    # reservations_manager and resources_manager confirmations
                    # 

                    self.reservations_manager.confirm(session, first_waiting_reservation.reservation_id)
                    slot_reservation = self.resources_manager.acquire_resource(session, free_instance)
                    concrete_current_reservation = ConcreteCurrentReservation(slot_reservation, first_waiting_reservation.reservation_id, 
                                                first_waiting_reservation.time, self.time_provider.get_time(), first_waiting_reservation.priority, first_waiting_reservation.client_initial_data)

                    client_initial_data = first_waiting_reservation.client_initial_data

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
                    except IntegrityError, ie:
                        # Other scheduler confirmed the user or booked the reservation, rollback and try again
                        # But log just in case
                        log.log(
                            PriorityQueueScheduler, LogLevel.Warning,
                            "IntegrityError looping on update_queues: %s" % ie )
                        log.log_exc(PriorityQueueScheduler, LogLevel.Info)
                        session.rollback()
                        break
                    except Exception, e:
                        log.log(
                            PriorityQueueScheduler, LogLevel.Warning,
                            "Exception looping on update_queues: %s" % e )
                        log.log_exc(PriorityQueueScheduler, LogLevel.Info)
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
                        server_initial_data = None 
                        # server_initial_data will contain information such as "what was the last experiment used?".
                        # If a single resource was used by a binary experiment, then the next time may not require reprogramming the device
                        self.confirmer.enqueue_confirmation(laboratory_coord_address, reservation_id, experiment_instance_id, client_initial_data, server_initial_data)
                        # 
                        # After it, keep in the while True in order to add the next 
                        # reservation
                        # 
                        break
            except IntegrityError, ie:
                # Something happened somewhere else, such as the user being confirmed twice, the experiment being reserved twice or so on.
                # Rollback and start again
                log.log(
                    PriorityQueueScheduler, LogLevel.Warning,
                    "IntegrityError: %s" % ie )
                log.log_exc(PriorityQueueScheduler, LogLevel.Info)
                session.rollback()
            finally:
                session.close()


    ################################################
    #
    # Remove all reservations whose session has expired
    #
    # TODO: Move this code to the reservations manager. Here it doesn't make much
    # sense.
    def _remove_expired_reservations(self):
        session = self.session_maker()
        try:
            now = self.time_provider.get_time()
            current_expiration_time = datetime.datetime.utcfromtimestamp(now - EXPIRATION_TIME)

            reservations_removed = False
            for expired_concrete_current_reservation in session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.start_time.op('+')(ConcreteCurrentReservation.time) < self.time_provider.get_time()).all():
                expired_reservation = expired_concrete_current_reservation.current_reservation_id
                if expired_reservation is None:
                    continue # Maybe it's not an expired_reservation anymore
                self._clean_current_reservation(session, expired_concrete_current_reservation)
                session.delete(expired_concrete_current_reservation)
                self.reservations_manager.delete(session, expired_reservation)
                reservations_removed = True

            for expired_reservation_id in self.reservations_manager.list_expired_reservations(session, current_expiration_time):
                concrete_current_reservation = session.query(ConcreteCurrentReservation).filter(ConcreteCurrentReservation.current_reservation_id == expired_reservation_id).first()
                if concrete_current_reservation is not None:
                    self._clean_current_reservation(session, concrete_current_reservation)
                    session.delete(concrete_current_reservation)
                waiting_reservation = session.query(WaitingReservation).filter(WaitingReservation.reservation_id == expired_reservation_id).first()
                if waiting_reservation is not None:
                    session.delete(waiting_reservation)

                self.reservations_manager.delete(session, expired_reservation_id)
                reservations_removed = True

            if reservations_removed:
                try:
                    session.commit()
                except sqlalchemy.exceptions.ConcurrentModificationError, e:
                    log.log(
                        PriorityQueueScheduler, LogLevel.Warning,
                        "IntegrityError: %s" % e )
                    log.log_exc(PriorityQueueScheduler, LogLevel.Info)
                    pass # Someone else removed these users before us.
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
        except sqlalchemy.exceptions.ConcurrentModificationError:
            pass # Another process is cleaning concurrently
        finally:
            session.close()


