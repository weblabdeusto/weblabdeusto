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

from abc import ABCMeta, abstractmethod

import weblab.configuration_doc as configuration_doc

class GenericSchedulerArguments(object):
    def __init__(self, cfg_manager, resource_type_name, reservations_manager, resources_manager, confirmer, data_manager, time_provider, core_server_url, initial_store, finished_store, completed_store, post_reservation_data_manager, **kwargs):
        self.cfg_manager          = cfg_manager
        self.resource_type_name   = resource_type_name
        self.reservations_manager = reservations_manager
        self.resources_manager    = resources_manager
        self.confirmer            = confirmer
        self.data_manager         = data_manager
        self.time_provider        = time_provider
        self.core_server_url      = core_server_url
        self.initial_store        = initial_store
        self.finished_store       = finished_store
        self.completed_store      = completed_store
        self.post_reservation_data_manager = post_reservation_data_manager

        if 'enqueuing_timeout' in kwargs:
            self.confirmer.enqueuing_timeout = kwargs.pop('enqueuing_timeout')
        if len(kwargs) > 0:
            raise RuntimeError("Unrecognized arguments: %s" % kwargs)

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

    __metaclass__ = ABCMeta

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
        # resources_manager is the Resources Manager. You can perform operations
        # with experiment instances, experiment types, resources, etc.
        #
        self.resources_manager    = generic_scheduler_arguments.resources_manager


        #
        # A data manager. It can be a redis client creator or a sqlalchemy session maker. 
        # It is already configured, so you can directly use it to create new sessions and 
        # perform changes against the database or the redis database. As long as you
        # have used sqlalchemy in your tables, and added your module to CoordinatorModel.load,
        # you will be able to use it. Otherwise, your scheduler should use another system and
        # require to configure it through the cfg_manager
        #
        self.session_maker        = generic_scheduler_arguments.data_manager
        self.data_manager         = generic_scheduler_arguments.data_manager
        self.redis_maker          = generic_scheduler_arguments.data_manager

        #
        # An instance of Coordinator.TimeProvider. It provides the time in different formats,
        # and it is easy to override while testing. As long as you are going to develop tests,
        # you should use it.
        #
        self.time_provider        = generic_scheduler_arguments.time_provider

        #
        # The Resource Type of the experiment being managed by this scheduler.
        #
        self.resource_type_name   = generic_scheduler_arguments.resource_type_name

        #
        # The address of the core server, such as 'https://www.weblab.deusto.es/weblab/',
        # so as to point out where is the server
        #
        self.core_server_url      = generic_scheduler_arguments.core_server_url

        self.core_server_route    = self.cfg_manager.get_doc_value(configuration_doc.CORE_FACADE_SERVER_ROUTE)

        self.core_server_uuid       = self.cfg_manager.get_value(configuration_doc.CORE_UNIVERSAL_IDENTIFIER)
        self.core_server_uuid_human = self.cfg_manager.get_value(configuration_doc.CORE_UNIVERSAL_IDENTIFIER_HUMAN)

        self.completed_store = generic_scheduler_arguments.completed_store

        self.post_reservation_data_manager = generic_scheduler_arguments.post_reservation_data_manager

    def stop(self):
        pass

    @abstractmethod
    def is_remote(self):
        pass

    ####################################################################################
    #
    # Experiment resources management. They should be implemented if the experiment
    # developer wants the users to administrate the resources through the WebLab
    # administration panel. Otherwise, the scheduler should handle the notifications
    # of "experiment broken", "experiment fixed", etc.
    #
    def removing_current_resource_slot(self, session, resource_instance_id):
        pass

    #######################################
    #
    # Kernel of the reservations
    #
    #
    @abstractmethod
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info):
        pass

    @abstractmethod
    def get_reservation_status(self, reservation_id):
        pass

    @abstractmethod
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration, exp_info):
        pass

    @abstractmethod
    def finish_reservation(self, reservation_id):
        pass

    def get_uuids(self):
        return []

    # Not abstract since most schedulers will not have it.
    def assign_single_scheduler(self, reservation_id, assigned_resource_type_name, locking):
        return []

    #############################################################
    #
    # Auxiliar method, used by tests to create a new scenario.
    #
    def _clean(self):
        pass

