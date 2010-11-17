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

class GenericSchedulerArguments(object):
     def __init__(self, cfg_manager, experiment_id, reservations_manager, confirmer, session_maker, time_provider):
        self.cfg_manager          = cfg_manager
        self.experiment_id        = experiment_id
        self.reservations_manager = reservations_manager
        self.confirmer            = confirmer
        self.session_maker        = session_maker
        self.time_provider        = time_provider

###################################################################
# 
# Scheduler is the basic abstract class from which all schedulers
# inherit. It provides the generic scheduler arguments to all the
# implementations, and defines the interface that will be used by
# the Coordinator.
# 
# In order to implement a new scheduler, implement this interface
# and add your model to the "CoordinatorModel.load" method. As long
# as it uses CoordinatorModel.Base as sqlalchemy Base, it will be
# deployed by the WebLab deployment tools, and managed with the 
# coordinator configuration parameters.
# 
# XXX The interface below has been extracted from PriorityQueueScheduler, the original WebLab-Deusto scheduler. It will change to support other schemas.
# 
class Scheduler(object):
    def __init__(self, generic_scheduler_arguments):
        #
        # cfg_manager is the Configuration Manager. It provides general configuration,
        # managed by the system.
        # 
        self.cfg_manager          = generic_scheduler_arguments.cfg_manager

        # 
        # confirmer is the Reservation Confirmer. You can enqueue confirmation requests
        # to the laboratory servers, so they can check if the experiment is running or
        # there is a problem in the system or in the network. These requests will be 
        # managed in an asynchronous basis.
        # 
        self.confirmer            = generic_scheduler_arguments.confirmer

        # 
        # reservations_manager is the Reservations Manager. You can create, delete, 
        # list, or modify reservations through this object. It ensures that the reservation
        # identifiers are unique among the different scheduling schemas.
        # 
        self.reservations_manager = generic_scheduler_arguments.reservations_manager

        # 
        # An sqlalchemy session_maker. It is already configured, so you can directly use
        # it to create new sessions and perform changes against the database. As long as you
        # have used sqlalchemy in your tables, and added your module to CoordinatorModel.load,
        # you will be able to use it. Otherwise, your scheduler should use another system and
        # require to configure it through the cfg_manager
        # 
        self.session_maker        = generic_scheduler_arguments.session_maker

        # 
        # An instance of Coordinator.TimeProvider. It provides the time in different formats,
        # and it is easy to override while testing. As long as you are going to develop tests,
        # you should use it.
        # 
        self.time_provider        = generic_scheduler_arguments.time_provider

        # 
        # The Experiment Identifier of the experiment being managed by this scheduler.
        # 
        self.experiment_id        = generic_scheduler_arguments.experiment_id

    #
    # TODO: 
    #  1. Batch experiments (add to "reserve" an additional argument)
    #  2. Broken experiments management ("fixed_experiment" method, "how are the experiments doing", "check every minute the broken experiments", etc. even through monitor.py)
    #  3. Añadir información más genérica tipo "este experimento está esperando a ser usado", del cual puedan heredar "está en cola" o "está planificado", etc. etc.
    # 

    ####################################################################################
    # 
    # Experiment resources management. They should be implemented if the experiment 
    # developer wants the users to administrate the resources through the WebLab 
    # administration panel. Otherwise, the scheduler should handle the notifications
    # of "experiment broken", "experiment fixed", etc.
    # 
    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id):
        pass

    def remove_experiment_instance_id(self, experiment_instance_id):
        pass

    def list_experiments(self):
        pass

    def list_sessions(self):
        pass

    #######################################
    # 
    # Kernel of the reservations
    # 
    # 
    def reserve_experiment(self, time, priority, initial_data):
        pass

    def get_reservation_status(self, reservation_id):
        pass

    def confirm_experiment(self, reservation_id, lab_session_id):
        pass

    def finish_reservation(self, reservation_id):
        pass

    #############################################################
    #
    # Auxiliar method, used by tests to create a new scenario.
    # 
    def _clean(self):
        pass

