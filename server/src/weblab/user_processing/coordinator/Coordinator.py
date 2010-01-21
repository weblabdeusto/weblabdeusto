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

import time
import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import not_

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.sessions.SessionId as SessionId

from weblab.user_processing.coordinator.dao import ExperimentType, ExperimentInstance, Reservation, CurrentReservation, WaitingReservation
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc
import weblab.user_processing.coordinator.WebLabQueueStatus as WQS
import weblab.user_processing.coordinator.Confirmer as Confirmer

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

COORDINATOR_DB_USERNAME   = 'core_coordinator_db_username'
COORDINATOR_DB_PASSWORD   = 'core_coordinator_db_password'
COORDINATOR_DB_HOST       = 'core_coordinator_db_host'
COORDINATOR_DB_NAME       = 'core_coordinator_db_name'
COORDINATOR_DB_ENGINE     = 'core_coordinator_db_engine'

DEFAULT_COORDINATOR_DB_HOST   = 'localhost'
DEFAULT_COORDINATOR_DB_NAME   = 'WebLabCoordination'
DEFAULT_COORDINATOR_DB_ENGINE = 'mysql' # The only one tested at the moment

def getconn():
    import MySQLdb as dbi
    return dbi.connect(user = Coordinator.username, passwd = Coordinator.password, 
                        host = Coordinator.host, db = Coordinator.dbname, client_flag = 2)


class Coordinator(object):

    username = None
    password = None
    host     = None
    db       = None

    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20)

    def __init__(self, locator, cfg_manager, ConfirmerClass = Confirmer.ReservationConfirmer):

        self.confirmer = ConfirmerClass(self, locator)

        engine   = cfg_manager.get_value(COORDINATOR_DB_ENGINE,  DEFAULT_COORDINATOR_DB_ENGINE)
        username = Coordinator.username = cfg_manager.get_value(COORDINATOR_DB_USERNAME) # REQUIRED!
        password = Coordinator.password = cfg_manager.get_value(COORDINATOR_DB_PASSWORD) # REQUIRED!
        host     = Coordinator.host     = cfg_manager.get_value(COORDINATOR_DB_HOST,    DEFAULT_COORDINATOR_DB_HOST)
        dbname   = Coordinator.dbname   = cfg_manager.get_value(COORDINATOR_DB_NAME,    DEFAULT_COORDINATOR_DB_NAME)

        sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine, username, password, host, dbname)

        engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, pool = self.pool)

        self._session_maker = sessionmaker(bind=engine, autoflush = True, autocommit = False)


    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id):
        session = self._session_maker()

        experiment_id = experiment_instance_id.to_experiment_id()
        experiment_type = ExperimentType(experiment_id.exp_name, experiment_id.cat_name)
        session.add(experiment_type)
        try:
            session.commit()
        except sqlalchemy.exceptions.IntegrityError:
            # Maybe it's already there
            session.rollback()
        session.close()

        session = self._session_maker()
        # 
        # At this point, we know that the experiment type is in the database.
        # 
        experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()

        experiment_instance = ExperimentInstance(experiment_type, laboratory_coord_address, experiment_instance_id.inst_name)

        session.add(experiment_instance)

        try:
            session.commit()
            session.close()
        except sqlalchemy.exceptions.IntegrityError:
            session.rollback()
            session.close()
            session = self._session_maker()
            experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()
            experiment_instance = session.query(ExperimentInstance).filter_by(experiment_type = experiment_type, experiment_instance_id = experiment_instance_id.inst_name).first()
            retrieved_laboratory_coord_address = experiment_instance.laboratory_coord_address
            if experiment_instance.laboratory_coord_address != laboratory_coord_address:
                session.close()
                raise CoordExc.InvalidExperimentConfigException("Attempt to register the experiment %s in the laboratory %s; this experiment is already registered in the laboratory %s" % (experiment_instance_id, laboratory_coord_address, retrieved_laboratory_coord_address))
            session.close()

    def remove_experiment_instance_id(self, experiment_instance_id):
        session = self._session_maker()

        experiment_id = experiment_instance_id.to_experiment_id()

        experiment_instance = session.query(ExperimentInstance)\
            .filter(ExperimentInstance.experiment_type_id     == ExperimentType.id)\
            .filter(ExperimentInstance.experiment_instance_id == experiment_instance_id.inst_name)\
            .filter(ExperimentType.exp_name                   == experiment_id.exp_name)\
            .filter(ExperimentType.cat_name                   == experiment_id.cat_name).one()

        current_reservation = experiment_instance.current_reservation
        if current_reservation is not None:
            #print "Downgrading to WaitingReservation..."
            waiting_reservation = WaitingReservation(experiment_instance.experiment_type, current_reservation.reservation, current_reservation.time,
                    -1 ) # -1 : Highest priority
            session.add(waiting_reservation)
            session.delete(current_reservation)

        session.delete(experiment_instance)

        session.commit()
        session.close()

    def list_experiments(self):
        session = self._session_maker()

        experiment_types = session.query(ExperimentType).order_by(ExperimentType.id).all()

        experiment_ids = []

        for experiment_type in experiment_types:
            experiment_ids.append(experiment_type.to_experiment_id())

        session.close()

        return experiment_ids


    def list_sessions(self, experiment_id):
        """ list_sessions( experiment_id ) -> { session_id : status } """
        session = self._session_maker()

        experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()
        if experiment_type is None:
            raise CoordExc.ExperimentNotFoundException("Experiment %s not found" % experiment_id)

        reservations = {}

        reservation_ids = []
        for instance in experiment_type.instances:
            for current_reservation in instance.current_reservations:
                reservation_ids.append(current_reservation.reservation.id)


        for waiting_reservation in experiment_type.waiting_reservations:
            reservation_ids.append(waiting_reservation.reservation.id)

        session.close()

        for reservation_id in reservation_ids:
            status = self.get_reservation_status(reservation_id)
            reservations[reservation_id] = status

        return reservations


    def reserve_experiment(self, experiment_id, time, priority):
        """
        priority: the less, the more priority
        """
        session = self._session_maker()

        experiment_type = session.query(ExperimentType).filter_by(exp_name = experiment_id.exp_name, cat_name = experiment_id.cat_name).first()
        if experiment_type is None:
            raise CoordExc.ExperimentNotFoundException("Experiment %s not found" % experiment_id)

        reservation         = Reservation(self._get_datetime)
        waiting_reservation = WaitingReservation(experiment_type, reservation, time, priority)
        session.add(waiting_reservation)

        session.commit()

        reservation_id = reservation.id

        session.close()

        return self.get_reservation_status(reservation_id), reservation_id



    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    def get_reservation_status(self, reservation_id):
        self._remove_expired_reservations()

        session = self._session_maker()

        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation is None:
            session.close()
            raise CoordExc.ExpiredSessionException("Expired reservation")
        else:
            reservation.update()
    
        waiting_reservation = reservation.waiting_reservation
        if waiting_reservation is not None:
            experiment_type_id = waiting_reservation.experiment_type.id
        else:
            current_reservation = reservation.current_reservation
            experiment_type_id  = None
            if current_reservation is not None:
                experiment_instance = current_reservation.experiment_instance
                if experiment_instance is not None:
                    experiment_type_id = experiment_instance.experiment_type.id
                    
            if experiment_type_id is None:
                session.close()
                raise Exception("Invalid state: reservation must have either a waiting_reservation or a current_reservation with an experiment_instance. Check if you're using tables without transactions or similar")

        session.commit()
        session.close()

        self._update_queues(experiment_type_id)

        session = self._session_maker()
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()

        # 
        # If the current user is actually in a reservation assigned to a 
        # certain laboratory, it may be in a Reserved state or in a 
        # WaitingConfirmation state (meaning that it is still waiting for
        # a response from the Laboratory).
        # 
        current_reservation = reservation.current_reservation
        if current_reservation is not None:
            experiment_instance = current_reservation.experiment_instance
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

        waiting_reservation = reservation.waiting_reservation
      
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
    def confirm_experiment(self, reservation_id, lab_session_id):
        self._remove_expired_reservations()

        session = self._session_maker()
        
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation is None:
            session.close()
            return

        if reservation.current_reservation is None:
            session.close()
            return

        reservation.current_reservation.lab_session_id = lab_session_id.id

        session.commit()
        session.close()


    ################################################################
    #
    # Called when the user disconnects or finishes the experiment.
    #
    def finish_reservation(self, reservation_id):
        self._remove_expired_reservations()

        session = self._session_maker()
        
        reservation_to_finish = session.query(Reservation).filter(Reservation.id == reservation_id).first()

        if reservation_to_finish is not None:
            current_reserv = reservation_to_finish.current_reservation
            if current_reserv is not None:
                experiment_instance = current_reserv.experiment_instance
                if experiment_instance is not None:
                    lab_session_id     = current_reserv.lab_session_id
                    lab_coord_address  = experiment_instance.laboratory_coord_address
                    self.confirmer.enqueue_free_experiment(lab_coord_address, lab_session_id)

            session.delete(reservation_to_finish.current_reservation or reservation_to_finish.waiting_reservation) # XXX: not required if ON DELETE CASCADE
            session.delete(reservation_to_finish)

        session.commit()
        session.close()



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
            session = self._session_maker()
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
            free_instances = session.query(ExperimentInstance)\
                    .filter(not_(ExperimentInstance.current_reservations.any()))\
                    .filter(ExperimentInstance.experiment_type == experiment_type)\
                    .order_by(ExperimentInstance.id).all()

            #
            # Add the waiting reservation to the db
            # 
            for free_instance in free_instances:
                #print "Creating CurrentReservation..."
                current_reservation = CurrentReservation(free_instance, first_waiting_reservation.reservation, 
                                            first_waiting_reservation.time, self._get_time(), first_waiting_reservation.priority)

                reservation = first_waiting_reservation.reservation
                if reservation is None:
                    break # If suddenly the waiting_reservation is not a waiting_reservation anymore, so reservation is None, go again to the while True.

                reservation_id = reservation.id
                experiment_type = free_instance.experiment_type
                if experiment_type is None:
                    continue # If suddenly the free_instance is not a free_instance anymore, try with other free_instance

                experiment_instance_id = ExperimentInstanceId(free_instance.experiment_instance_id, experiment_type.exp_name, experiment_type.cat_name)

                laboratory_coord_address = free_instance.laboratory_coord_address
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
        session = self._session_maker()

        now = self._get_time()
        current_expiration_time = datetime.datetime.utcfromtimestamp(now - EXPIRATION_TIME)

        reservations_removed = False
        for current_expired_reservation in session.query(CurrentReservation).filter(CurrentReservation.start_time.op('+')(CurrentReservation.time) < self._get_time()).all():
            expired_reservation = current_expired_reservation.reservation
            if expired_reservation is None:
                continue # Maybe it's not an expired_reservation anymore
            session.delete(current_expired_reservation)
            session.delete(expired_reservation)
            reservations_removed = True

        for expired_reservation in session.query(Reservation).filter(Reservation.latest_access < current_expiration_time).all():
            # XXX: Removing current_reservation and waiting_reservation is not required if ON DELETE CASCADE
            current_reservation = expired_reservation.current_reservation
            if current_reservation is not None:
                session.delete(current_reservation)
            waiting_reservation = expired_reservation.waiting_reservation
            if waiting_reservation is not None:
                session.delete(waiting_reservation)

            session.delete(expired_reservation)
            reservations_removed = True

        if reservations_removed:
            try:
                session.commit()
            except sqlalchemy.exceptions.ConcurrentModificationError:
                pass # Someone else removed these users before us.
        else:
            session.rollback()
        session.close()

    def _get_time(self):
        return time.time()

    def _get_datetime(self):
        return datetime.datetime.utcnow()

    ##############################################################
    # 
    # ONLY FOR TESTING: It completely removes the whole database
    # 
    def _clean(self):
        session = self._session_maker()
    
        try:
            for waiting_reservation in session.query(WaitingReservation).all():
                session.delete(waiting_reservation)
            for current_reservation in session.query(CurrentReservation).all():
                session.delete(current_reservation)
            for experiment_instance in session.query(ExperimentInstance).all():
                session.delete(experiment_instance)

            for experiment_type in session.query(ExperimentType).all():
                session.delete(experiment_type)
            for reservation in session.query(Reservation).all():
                session.delete(reservation)

            session.commit()
        except sqlalchemy.exceptions.ConcurrentModificationError:
            pass # Another process is cleaning concurrently
        session.close()


