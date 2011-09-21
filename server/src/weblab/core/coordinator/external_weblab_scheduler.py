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

from voodoo.override import Override
from weblab.core.coordinator.scheduler import Scheduler
from voodoo.log import logged

class ExternalWebLabScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, **kwargs):
        super(ExternalWebLabScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

    def stop(self):
        pass

    @logged()
    @Override(Scheduler)
    def removing_current_resource_slot(self, session, resource_instance_id):
        return False

    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting):
        return self.get_reservation_status(reservation_id)

    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        # TODO
        raise NotImplementedError("")


    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration):
        pass

    ################################################################
    #
    # Called when the user disconnects or finishes the resource.
    #
    @logged()
    @Override(Scheduler)
    def finish_reservation(self, reservation_id):
        pass

    ##############################################################
    # 
    # ONLY FOR TESTING: It completely removes the whole database
    # 
    @Override(Scheduler)
    def _clean(self):
        pass

