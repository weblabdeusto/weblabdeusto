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

import sqlalchemy
from sqlalchemy import not_
from sqlalchemy.orm import join

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.sessions.SessionId as SessionId
from voodoo.override import Override

from weblab.user_processing.coordinator.Scheduler import Scheduler
from weblab.user_processing.coordinator.PriorityQueueSchedulerModel import ExperimentType, ExperimentInstance, CurrentReservation, WaitingReservation, AvailableExperimentInstance
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc
import weblab.user_processing.coordinator.WebLabQueueStatus as WQS

from weblab.data.experiments.ExperimentInstanceId import ExperimentInstanceId


EXPIRATION_TIME  = 3600 # seconds

###########################################################
# 
# There are types of experiments and instances of these 
# types. ExperimentType identifies the types of experiments,
# with a Category Name and a Experiment Name. This way, if
# there are 4 different PLD experiments, you can describe
# them with a Category called "PLD experiments" and with a
# experiment name of "ud-pld". 
# 
# Then, you can have different instances of these 
# experiments, which will be the different real experiments 
# deployed. Each of these experiments will have a unique
# identifier per experiment type. This way, we might have
# 2 experiments of "ud-pld" deployed, one in the room 007 
# and another in the room 505 of the faculty. We will then
# have an instance "instance.505" of type ud-pld.
# 
# This way, the coordinator balances the load of the users
# among the different instances of a certain Experiment
# Type. If there are 4 instances of the type ud-pld and 
# there are 5 users trying to use that type of experiment,
# then 4 users will start using it, and the other one will 
# be in a global queue of that experiment type. As soon as
# one user finishes, the 5th user will start using that
# instance.
# 

class PriorityQueueScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments):
        super(PriorityQueueScheduler, self).__init__(generic_scheduler_arguments)

    @Override(Scheduler)
    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id):
        session = self.session_maker()

        experiment_id = experiment_instance_id.to_experiment_id()
        experiment_type = ExperimentType(experiment_id.exp_name, experiment_id.cat_name)
        session.add(experiment_type)
        try:
            session.commit()
        except sqlalchemy.exceptions.IntegrityError:
            # Maybe it's already there
            session.rollback()
        session.close()

        session = self.session_maker()
        # 
        # At this point, we know that the experiment type is in the database.
        # 
        experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()

        experiment_instance = ExperimentInstance(experiment_type, laboratory_coord_address, experiment_instance_id.inst_name)

        session.add(experiment_instance)

        available_experiment_instance = AvailableExperimentInstance(experiment_instance)

        session.add(available_experiment_instance)

        try:
            session.commit()
            session.close()
        except sqlalchemy.exceptions.IntegrityError:
            session.rollback()
            session.close()
            session = self.session_maker()
            experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()
            experiment_instance = session.query(ExperimentInstance).filter_by(experiment_type = experiment_type, experiment_instance_id = experiment_instance_id.inst_name).first()
            retrieved_laboratory_coord_address = experiment_instance.laboratory_coord_address
            if experiment_instance.laboratory_coord_address != laboratory_coord_address:
                session.close()
                raise CoordExc.InvalidExperimentConfigException("Attempt to register the experiment %s in the laboratory %s; this experiment is already registered in the laboratory %s" % (experiment_instance_id, laboratory_coord_address, retrieved_laboratory_coord_address))
            session.close()

    @Override(Scheduler)
    def remove_experiment_instance_id(self, experiment_instance_id):
        session = self.session_maker()

        experiment_id = experiment_instance_id.to_experiment_id()

        experiment_instance = session.query(ExperimentInstance)\
            .filter(ExperimentInstance.experiment_type_id     == ExperimentType.id)\
            .filter(ExperimentInstance.experiment_instance_id == experiment_instance_id.inst_name)\
            .filter(ExperimentType.exp_name                   == experiment_id.exp_name)\
            .filter(ExperimentType.cat_name                   == experiment_id.cat_name).one()

        available_experiment_instance = experiment_instance.available

        if available_experiment_instance is not None:

            current_reservation = available_experiment_instance.current_reservation
            if current_reservation is not None:
                #print "Downgrading to WaitingReservation..."
                waiting_reservation = WaitingReservation(experiment_instance.experiment_type, current_reservation.reservation_id, current_reservation.time,
                        -1, current_reservation.initial_data ) # -1 : Highest priority
                session.add(waiting_reservation)
                session.delete(current_reservation)

            session.delete(available_experiment_instance)

        session.delete(experiment_instance)

        session.commit()
        session.close()

    @Override(Scheduler)
    def list_experiments(self):
        session = self.session_maker()

        experiment_types = session.query(ExperimentType)\
                            .filter(ExperimentType.exp_name == self.experiment_id.exp_name)\
                            .filter(ExperimentType.cat_name == self.experiment_id.cat_name)\
                            .order_by(ExperimentType.id).all()

        experiment_ids = []

        for experiment_type in experiment_types:
            experiment_ids.append(experiment_type.to_experiment_id())

        session.close()

        return experiment_ids


    @Override(Scheduler)
    def list_sessions(self):
        """ list_sessions( experiment_id ) -> { session_id : status } """
        session = self.session_maker()

        experiment_type = session.query(ExperimentType).filter_by(exp_name = self.experiment_id.exp_name, cat_name = self.experiment_id.cat_name).first()
        if experiment_type is None:
            raise CoordExc.ExperimentNotFoundException("Experiment %s not found" % self.experiment_id)

        reservations = {}

        reservation_ids = []
        for instance in experiment_type.instances:
            available_instance = instance.available
            if available_instance is not None:
                for current_reservation in available_instance.current_reservations:
                    reservation_ids.append(current_reservation.reservation_id)


        for waiting_reservation in experiment_type.waiting_reservations:
            reservation_ids.append(waiting_reservation.reservation_id)

        session.close()

        for reservation_id in reservation_ids:
            status = self.get_reservation_status(reservation_id)
            reservations[reservation_id] = status

        return reservations


    @Override(Scheduler)
    def reserve_experiment(self, time, priority, initial_data):
        """
        priority: the less, the more priority
        """
        session = self.session_maker()

        experiment_type = session.query(ExperimentType).filter_by(exp_name = self.experiment_id.exp_name, cat_name = self.experiment_id.cat_name).first()
        if experiment_type is None:
            raise CoordExc.ExperimentNotFoundException("Experiment %s not found" % self.experiment_id)

        session.close()

        reservation_id = self.reservations_manager.create(self.experiment_id.to_weblab_str(), self.time_provider.get_datetime)

        session = self.session_maker()
        waiting_reservation = WaitingReservation(experiment_type, reservation_id, time, priority, initial_data)
        session.add(waiting_reservation)

        session.commit()

        session.close()

        return self.get_reservation_status(reservation_id), reservation_id



    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        self._remove_expired_reservations()

        session = self.session_maker()

        self.reservations_manager.update(session, reservation_id)
    
        waiting_reservation = session.query(WaitingReservation).filter(WaitingReservation.reservation_id == reservation_id).first()
        if waiting_reservation is not None:
            experiment_type_id = waiting_reservation.experiment_type.id
        else:
            current_reservation = session.query(CurrentReservation).filter(CurrentReservation.reservation_id == reservation_id).first()
            experiment_type_id  = None
            if current_reservation is not None:
                experiment_instance = current_reservation.available_experiment_instance.experiment_instance
                if experiment_instance is not None:
                    experiment_type_id = experiment_instance.experiment_type.id
                    
            if experiment_type_id is None:
                session.close()
                raise Exception("Invalid state: reservation must have either a waiting_reservation or a current_reservation with an experiment_instance. Check if you're using tables without transactions or similar")

        session.commit()
        session.close()

        self._update_queues(experiment_type_id)

        session = self.session_maker()

        # 
        # If the current user is actually in a reservation assigned to a 
        # certain laboratory, it may be in a Reserved state or in a 
        # WaitingConfirmation state (meaning that it is still waiting for
        # a response from the Laboratory).
        # 
        current_reservation = session.query(CurrentReservation).filter(CurrentReservation.reservation_id == reservation_id).first()
        if current_reservation is not None:
            experiment_instance   = current_reservation.available_experiment_instance.experiment_instance
            str_lab_coord_address = experiment_instance.laboratory_coord_address
            lab_coord_address     = CoordAddress.CoordAddress.translate_address(str_lab_coord_address)
            obtained_time         = current_reservation.time
            lab_session_id        = current_reservation.lab_session_id
            if lab_session_id is None:
                status = WQS.WaitingConfirmationQueueStatus(lab_coord_address, obtained_time)
            else:
                status = WQS.ReservedQueueStatus(lab_coord_address, SessionId.SessionId(lab_session_id), obtained_time)

            session.close()
            return status

        waiting_reservation = session.query(WaitingReservation).filter(WaitingReservation.reservation_id == reservation_id).first()
      
        # 
        # If it has not been assigned to any laboratory, then it might
        # be waiting in the queue of that experiment type (Waiting) or 
        # waiting for instances (WaitingInstances, meaning that there is
        # no experiment of that type implemented)
        # 
        waiting_reservations = session.query(WaitingReservation)\
                .filter(WaitingReservation.experiment_type == waiting_reservation.experiment_type).order_by(WaitingReservation.priority, WaitingReservation.id).all()

        if waiting_reservation is None or waiting_reservation not in waiting_reservations:
            # 
            # The position has changed and it is not in the list anymore! 
            # This has happened using WebLab Bot with 65 users.
            # 
            session.close()
            return self.get_reservation_status(reservation_id)

        position      = waiting_reservations.index(waiting_reservation)
        instance_number = len(waiting_reservation.experiment_type.instances)

        session.close()

        if instance_number == 0:
            return WQS.WaitingInstancesQueueStatus(position)
        else:
            return WQS.WaitingQueueStatus(position)



    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id):
        self._remove_expired_reservations()

        session = self.session_maker()
        
        if not self.reservations_manager.check(session, reservation_id):
            session.close()
            return

        current_reservation = session.query(CurrentReservation).filter(CurrentReservation.reservation_id == reservation_id).first()
        if current_reservation is None:
            session.close()
            return

        current_reservation.lab_session_id = lab_session_id.id

        session.commit()
        session.close()


    ################################################################
    #
    # Called when the user disconnects or finishes the experiment.
    #
    @Override(Scheduler)
    def finish_reservation(self, reservation_id):
        self._remove_expired_reservations()

        session = self.session_maker()
        
        self.reservations_manager.delete(session, reservation_id)

        current_reservation = session.query(CurrentReservation).filter(CurrentReservation.reservation_id == reservation_id).first()

        self._clean_reservation(current_reservation)
            
        reservation_to_delete = current_reservation or session.query(WaitingReservation).filter(WaitingReservation.reservation_id == reservation_id).first()
        if reservation_to_delete is not None:
            session.delete(reservation_to_delete) 

            session.commit()
        session.close()

    def _clean_reservation(self, current_reservation):
        if current_reservation is not None:
            experiment_instance = current_reservation.available_experiment_instance.experiment_instance
            if experiment_instance is not None:
                lab_session_id     = current_reservation.lab_session_id
                lab_coord_address  = experiment_instance.laboratory_coord_address
                self.confirmer.enqueue_free_experiment(lab_coord_address, lab_session_id)

    #############################################################
    # 
    # Take the queue of a given Experiment Type and update it
    # 
    def _update_queues(self, experiment_type_id):
        ###########################################################
        # While there are free instances and waiting reservations, 
        # take the first waiting reservation and set it to current 
        # reservation. Make this repeatedly because we want to 
        # commit each change
        # 
        while True:
            session = self.session_maker()
            experiment_type = session.query(ExperimentType).filter(ExperimentType.id == experiment_type_id).first()

            # 
            # Retrieve the first waiting reservation. If there is no one,
            # return
            # 
            first_waiting_reservation = session.query(WaitingReservation).filter(WaitingReservation.experiment_type == experiment_type).order_by(WaitingReservation.priority, WaitingReservation.id).first()

            if first_waiting_reservation is None:
                session.close()
                return


            # 
            # For the current experiment_type, let's ask for 
            # all the experiment instances available (i.e. those
            # who have no CurrentReservation associated)
            # 
            free_instances = session.query(AvailableExperimentInstance)\
                    .select_from(join(AvailableExperimentInstance, ExperimentInstance))\
                    .filter(not_(AvailableExperimentInstance.current_reservations.any()))\
                    .filter(ExperimentInstance.experiment_type == experiment_type)\
                    .order_by(AvailableExperimentInstance.id).all()

            #
            # Add the waiting reservation to the db
            # 
            for free_instance in free_instances:
                #print "Creating CurrentReservation..."
                current_reservation = CurrentReservation(free_instance, first_waiting_reservation.reservation_id, 
                                            first_waiting_reservation.time, self.time_provider.get_time(), first_waiting_reservation.priority, first_waiting_reservation.initial_data)

                reservation_id = first_waiting_reservation.reservation_id
                if reservation_id is None:
                    break # If suddenly the waiting_reservation is not a waiting_reservation anymore, so reservation is None, go again to the while True.

                experiment_type = free_instance.experiment_instance.experiment_type
                if experiment_type is None:
                    continue # If suddenly the free_instance is not a free_instance anymore, try with other free_instance

                experiment_instance_id = ExperimentInstanceId(free_instance.experiment_instance.experiment_instance_id, experiment_type.exp_name, experiment_type.cat_name)

                laboratory_coord_address = free_instance.experiment_instance.laboratory_coord_address
                session.delete(first_waiting_reservation)
                session.add(current_reservation)
                try:
                    session.commit()
                except Exception:
                    session.rollback()
                else:
                    # 
                    # Enqueue the confirmation, since it might take a long time
                    # (for instance, if the laboratory server does not reply because
                    # of any network problem, or it just takes too much in replying),
                    # so this method might take too long. That's why we enqueue these
                    # petitions and run them in other threads.
                    # 
                    self.confirmer.enqueue_confirmation(laboratory_coord_address, reservation_id, experiment_instance_id)
                    # 
                    # After it, keep in the while True in order to add the next 
                    # reservation
                    # 
                    break
            else:
                # There is no free_instance, return
                session.close()
                return
            session.close()


    ################################################
    #
    # Remove all reservations whose session has expired
    #
    def _remove_expired_reservations(self):
        session = self.session_maker()

        now = self.time_provider.get_time()
        current_expiration_time = datetime.datetime.utcfromtimestamp(now - EXPIRATION_TIME)

        reservations_removed = False
        for current_expired_reservation in session.query(CurrentReservation).filter(CurrentReservation.start_time.op('+')(CurrentReservation.time) < self.time_provider.get_time()).all():
            expired_reservation = current_expired_reservation.reservation_id
            if expired_reservation is None:
                continue # Maybe it's not an expired_reservation anymore
            self._clean_reservation(current_expired_reservation)
            session.delete(current_expired_reservation)
            self.reservations_manager.delete(session, expired_reservation)
            reservations_removed = True

        for expired_reservation_id in self.reservations_manager.list_expired_reservations(session, current_expiration_time):
            current_reservation = session.query(CurrentReservation).filter(CurrentReservation.reservation_id == expired_reservation_id).first()
            if current_reservation is not None:
                self._clean_reservation(current_reservation)
                session.delete(current_reservation)
            waiting_reservation = session.query(WaitingReservation).filter(WaitingReservation.reservation_id == expired_reservation_id).first()
            if waiting_reservation is not None:
                session.delete(waiting_reservation)

            self.reservations_manager.delete(session, expired_reservation_id)
            reservations_removed = True

        if reservations_removed:
            try:
                session.commit()
            except sqlalchemy.exceptions.ConcurrentModificationError:
                pass # Someone else removed these users before us.
        else:
            session.rollback()
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
            for current_reservation in session.query(CurrentReservation).all():
                session.delete(current_reservation)
            for available_experiment_instance in session.query(AvailableExperimentInstance).all():
                session.delete(available_experiment_instance)
            for experiment_instance in session.query(ExperimentInstance).all():
                session.delete(experiment_instance)

            for experiment_type in session.query(ExperimentType).all():
                session.delete(experiment_type)

            session.commit()
        except sqlalchemy.exceptions.ConcurrentModificationError:
            pass # Another process is cleaning concurrently
        session.close()


