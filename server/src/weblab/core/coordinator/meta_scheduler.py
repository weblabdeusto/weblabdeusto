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


from voodoo.log import logged
from weblab.core.coordinator.scheduler import Scheduler
from voodoo.override import Override

##############################
#  XXX: this class will disappear soon
#    Temporal
# 
class MetaScheduler(object):
    def query_best_reservation_status(self, schedulers, reservation_id):
        if len(schedulers) == 0:
            raise ValueError("There must be at least one scheduler, zero provided!")

        all_reservation_status = []
        for scheduler in schedulers:
            reservation_status = scheduler.get_reservation_status(reservation_id)
            all_reservation_status.append(reservation_status)
        return self.select_best_reservation_status(all_reservation_status)

    def select_best_reservation_status(self, all_reservation_status):
        if len(all_reservation_status) == 0:
            raise ValueError("There must be at least one reservation status, zero provided!")

        all_reservation_status.sort()
        return all_reservation_status[0]

#############################################################
# 
# The Independent Scheduler Aggregator aggregates different 
# schedulers that schedule independent resources. For 
# instance, one experiment that can be executed in two 
# different types of "rigs" will be waiting in two queues
# at the same time. This class will handle established 
# policies such as priorities among schedulers.
# 
# Take into account that a possible scheduler is an external
# scheduler (such as another WebLab-Deusto). Therefore 
# policies can become complex here.
# 
# Therefore, while it is compliant with the Scheduler 
# API, it can not be configured as such in the core config
# files: it will be created by the coordinator in the 
# constructor, creating one per experiment_id.
# 
class IndependentSchedulerAggregator(Scheduler):

    def __init__(self, generic_scheduler_arguments, schedulers, particular_configuration):
        super(IndependentSchedulerAggregator, self).__init__(generic_scheduler_arguments)
        self.particular_configuration = particular_configuration

    def stop(self):
        pass

    @logged()
    @Override(Scheduler)
    def removing_current_resource_slot(self, session, resource_instance):
        pass

    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data):
        pass

    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        pass

    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration):
        pass

    @logged()
    @Override(Scheduler)
    def finish_reservation(self, reservation_id):
        pass

    @Override(Scheduler)
    def _clean(self):
        pass



class SharedSchedulerAggregator(object):
    pass


