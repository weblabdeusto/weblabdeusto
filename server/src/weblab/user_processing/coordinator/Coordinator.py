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

import weblab.data.experiments.ExperimentId as ExperimentId

import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc

import weblab.user_processing.coordinator.ReservationsManager as ReservationsManager
import weblab.user_processing.coordinator.Confirmer as Confirmer
import weblab.user_processing.coordinator.Scheduler as Scheduler

import weblab.user_processing.coordinator.PriorityQueueScheduler as PriorityQueueScheduler

PRIORITY_QUEUE = 'PRIORITY_QUEUE'

SCHEDULING_SYSTEMS = {
        PRIORITY_QUEUE : PriorityQueueScheduler.PriorityQueueScheduler
    }

CORE_SCHEDULING_SYSTEMS = 'core_scheduling_systems'


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

class TimeProvider(object):
    def get_time(self):
        return time.time()

    def get_datetime(self):
        return datetime.datetime.utcnow()

class Coordinator(object):

    username = None
    password = None
    host     = None
    db       = None

    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20)

    CoordinatorTimeProvider = TimeProvider


    def __init__(self, locator, cfg_manager, ConfirmerClass = Confirmer.ReservationConfirmer):

        engine   = cfg_manager.get_value(COORDINATOR_DB_ENGINE,  DEFAULT_COORDINATOR_DB_ENGINE)
        username = Coordinator.username = cfg_manager.get_value(COORDINATOR_DB_USERNAME) # REQUIRED!
        password = Coordinator.password = cfg_manager.get_value(COORDINATOR_DB_PASSWORD) # REQUIRED!
        host     = Coordinator.host     = cfg_manager.get_value(COORDINATOR_DB_HOST,    DEFAULT_COORDINATOR_DB_HOST)
        dbname   = Coordinator.dbname   = cfg_manager.get_value(COORDINATOR_DB_NAME,    DEFAULT_COORDINATOR_DB_NAME)

        sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine, username, password, host, dbname)

        engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, pool = self.pool)

        self._session_maker = sessionmaker(bind=engine, autoflush = True, autocommit = False)

        self.confirmer = ConfirmerClass(self, locator)
        self.reservations_manager = ReservationsManager.ReservationsManager(self._session_maker)
        self.time_provider = self.CoordinatorTimeProvider()

        # 
        # The system administrator must define what scheduling system is used by each experiment type
        # For instance:
        # 
        # scheduling_systems = {
        #                  "ud-pld@PLD Experiments"      : ("PRIORITY_QUEUE", {}),
        #                  "ud-fpga@FPGA Experiments"    : ("PRIORITY_QUEUE", {}),
        #                  "ud-other@Longer Experiments" : ("BOOKING", { 'slots' : 30 * 1000 }), # Slots of 30 minutes
        #                  "ud-other@Longer Experiments" : ("EXTERNAL", { 'address' : 'http://192.168.1.50:8080/SchedulingServer', 'protocol' : 'SOAP' }) # If somebody else has implemented the scheduling schema in other language
        #            }
        # 
        self.schedulers = {}
        scheduling_systems = cfg_manager.get_value(CORE_SCHEDULING_SYSTEMS)
        for experiment_id_str in scheduling_systems:
            scheduling_system, arguments = scheduling_systems[experiment_id_str]
            if not scheduling_system in SCHEDULING_SYSTEMS:
                raise CoordExc.UnregisteredSchedulingSystemException("Unregistered scheduling system: %s" % scheduling_system)
            SchedulingSystemClass = SCHEDULING_SYSTEMS[scheduling_system]
            experiment_id = ExperimentId.ExperimentId.parse(experiment_id_str)
            
            generic_scheduler_arguments = Scheduler.GenericSchedulerArguments(cfg_manager, experiment_id, self.reservations_manager, self.confirmer, self._session_maker, self.time_provider)

            self.schedulers[experiment_id_str] = SchedulingSystemClass(generic_scheduler_arguments, **arguments)

    ##########################################################################
    # 
    #   Methods to retrieve the proper schedulers
    # 
    def _get_scheduler_per_reservation(self, reservation_id):
        experiment_id = self.reservations_manager.get_experiment_id(reservation_id)
        return self.schedulers[experiment_id]

    def _get_scheduler_per_experiment_instance_id(self, experiment_instance_id):
        return self._get_scheduler_per_experiment_id(experiment_instance_id.to_experiment_id())

    def _get_scheduler_per_experiment_id(self, experiment_id):
        experiment_id_str = experiment_id.to_weblab_str()
        if experiment_id_str not in self.schedulers:
            raise CoordExc.ExperimentNotFoundException("Unregistered Experiment ID: %s. Check the %s property." % (experiment_id_str, CORE_SCHEDULING_SYSTEMS))
        return self.schedulers[experiment_id_str]

    ###########################################################################
    # 
    # General experiments and sessions management
    # 
    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id):
        scheduler = self._get_scheduler_per_experiment_instance_id(experiment_instance_id)
        return scheduler.add_experiment_instance_id(laboratory_coord_address, experiment_instance_id)

    def remove_experiment_instance_id(self, experiment_instance_id):
        scheduler = self._get_scheduler_per_experiment_instance_id(experiment_instance_id)
        return scheduler.remove_experiment_instance_id(experiment_instance_id)

    def list_experiments(self):
        experiments = []
        for scheduler in self.schedulers.values():
            experiments.extend(scheduler.list_experiments())
        return experiments

    def list_sessions(self, experiment_id):
        """ list_sessions( experiment_id ) -> { session_id : status } """
        scheduler = self._get_scheduler_per_experiment_id(experiment_id)
        return scheduler.list_sessions()

    ##########################################################################
    # 
    # Perform a new reservation
    # 
    def reserve_experiment(self, experiment_id, time, priority, initial_data):
        """
        priority: the less, the more priority
        """
        scheduler = self._get_scheduler_per_experiment_id(experiment_id)
        return scheduler.reserve_experiment(time, priority, initial_data)

    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    def get_reservation_status(self, reservation_id):
        scheduler = self._get_scheduler_per_reservation(reservation_id)
        return scheduler.get_reservation_status(reservation_id)

    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    def confirm_experiment(self, reservation_id, lab_session_id):
        scheduler = self._get_scheduler_per_reservation(reservation_id)
        return scheduler.confirm_experiment(reservation_id, lab_session_id)

    ################################################################
    #
    # Called when the user disconnects or finishes the experiment.
    #
    def finish_reservation(self, reservation_id):
        scheduler = self._get_scheduler_per_reservation(reservation_id)
        return scheduler.finish_reservation(reservation_id)

    def _clean(self):
        self.reservations_manager._clean()
        for scheduler in self.schedulers.values():
            scheduler._clean()


