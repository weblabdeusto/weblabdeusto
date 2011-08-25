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

from voodoo.threaded import threaded
import voodoo.log as log

import voodoo.resources_manager as ResourceManager
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.sessions.session_id as SessionId

import weblab.data.server_type as ServerType

_resource_manager = ResourceManager.CancelAndJoinResourceManager("Coordinator")

class ReservationConfirmer(object):
    def __init__(self, coordinator, locator):
        self.coordinator                        = coordinator
        self.locator                            = locator
        self._enqueuing_timeout                 = 0
        self._initialize_and_dispose_experiment = True

    def _get_enqueuing_timeout(self):
        return self._enqueuing_timeout

    def _set_enqueuing_timeout(self, value):
        self._enqueuing_timeout = value

    enqueuing_timeout = property(_get_enqueuing_timeout, _set_enqueuing_timeout)

    def enqueue_confirmation(self, lab_coordaddress_str, reservation_id, experiment_instance_id, client_initial_data, server_initial_data):
        # We can stablish a politic such as using 
        # thread pools or a queue of threads or something
        # like that... here
        lab_coordaddress = CoordAddress.CoordAddress.translate_address(lab_coordaddress_str)
        self._confirm_handler = self._confirm_experiment(lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data)
        self._confirm_handler.join(self._enqueuing_timeout)

    @threaded(_resource_manager)
    def _confirm_experiment(self, lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data):
        initial_time = datetime.datetime.now()
        try:
            labserver = self.locator.get_server_from_coordaddr(lab_coordaddress, ServerType.Laboratory)
            lab_session_id, server_initialization_response, experiment_coordaddress_str = labserver.reserve_experiment(experiment_instance_id, client_initial_data, server_initial_data)
        except Exception as e:
            log.log( ReservationConfirmer, log.LogLevel.Error, "Exception confirming experiment: %s" % e )
            log.log_exc( ReservationConfirmer, log.LogLevel.Warning )

            self.coordinator.mark_experiment_as_broken(experiment_instance_id, [str(e)])
        else:
            end_time = datetime.datetime.now()
            experiment_coordaddress = CoordAddress.CoordAddress.translate_address(experiment_coordaddress_str)
            self.coordinator.confirm_experiment(experiment_coordaddress, experiment_instance_id, reservation_id, lab_session_id, server_initialization_response, initial_time, end_time)

    def enqueue_free_experiment(self, lab_coordaddress_str, reservation_id, lab_session_id, experiment_instance_id):
        # We can stablish a policy such as using 
        # thread pools or a queue of threads or something
        # like that... here
        lab_coordaddress = CoordAddress.CoordAddress.translate_address(lab_coordaddress_str)
        if lab_session_id is None: # If the user didn't manage to obtain a session_id, don't call the free_experiment method
            experiment_response = None
            initial_time = end_time = datetime.datetime.now()
            self.coordinator.confirm_resource_disposal(lab_coordaddress_str, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time)
        else: # Otherwise...
            self._free_handler = self._free_experiment(lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id)
            self._free_handler.join(self._enqueuing_timeout)


    @threaded(_resource_manager)
    def _free_experiment(self, lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id):
        initial_time = datetime.datetime.now()
        try:
            labserver = self.locator.get_server_from_coordaddr(lab_coordaddress, ServerType.Laboratory)
            experiment_response = labserver.free_experiment(SessionId.SessionId(lab_session_id))
        except Exception as e:
            log.log( ReservationConfirmer, log.LogLevel.Error, "Exception freeing experiment: %s" % e )
            log.log_exc( ReservationConfirmer, log.LogLevel.Warning )

            self.coordinator.mark_experiment_as_broken(experiment_instance_id, [str(e)])
        else: # Everything went fine
            end_time = datetime.datetime.now()
            self.coordinator.confirm_resource_disposal(lab_coordaddress.address, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time)

