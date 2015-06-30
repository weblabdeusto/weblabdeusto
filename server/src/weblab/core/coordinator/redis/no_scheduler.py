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

from voodoo.override import Override

from weblab.core.coordinator.scheduler import Scheduler
from voodoo.log import logged

class NoScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, **kwargs):
        super(NoScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

    def stop(self):
        pass

    @Override(Scheduler)
    def is_remote(self):
        return False

    @logged()
    @Override(Scheduler)
    def removing_current_resource_slot(self, session, resource_instance_id):
        # Will in fact never be called
        return False

    def _reserved(self):
        reservation_id_with_route = '%s;%s.%s' % (reservation_id, reservation_id, self.core_server_route)

        #
        # TODO: will always be the same, even if there are plenty of them.
        # With no_scheduler, there is no load balance: all the users go
        # to the same experiment server.
        #
        lab_coord_address = ""
        exp_info = ""

        #
        # TODO: we must support at laboratory server level that several
        # sessions have access to the same experiment. Basically, always
        # trust the coordinator instead of checking it twice.
        #
        lab_session_id = 'TODO'

        #
        # TODO: we still have to retrieve these values, calling the
        # confirmator. But we can't even test this until the point
        # above is implemented!
        #
        obtained_time = 100
        remaining     = 100
        initial_configuration = ""
        timestamp_before = None
        timestamp_after  = None

        #
        # TODO: this must be retrieved from a no-scheduler specific
        # database
        #
        initialization_in_accounting = True

        return WSS.LocalReservedStatus(reservation_id_with_route, lab_coord_address, SessionId.SessionId(lab_session_id), exp_info, obtained_time, initial_configuration, timestamp_before, timestamp_after, initialization_in_accounting, remaining, self.core_server_url)


    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info):
        return self._reserved()

    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        return self._reserved()

    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration, exp_info):
        # At some point, we must call the upper level to say that we want to confirm
        # at this point, it's normal that they call us back, even if there is nothing
        # to do
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

