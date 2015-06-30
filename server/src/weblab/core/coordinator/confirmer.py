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

import datetime
import traceback

from voodoo.threaded import threaded
import voodoo.log as log
from voodoo.log import logged

import voodoo.resources_manager as ResourceManager
from voodoo.gen import CoordAddress
import voodoo.sessions.session_id as SessionId

_resource_manager = ResourceManager.CancelAndJoinResourceManager("Coordinator")

DEBUG = False

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

    @logged()
    def enqueue_confirmation(self, lab_coordaddress_str, reservation_id, experiment_instance_id, client_initial_data, server_initial_data, resource_type_name):
        # We can stablish a politic such as using
        # thread pools or a queue of threads or something
        # like that... here
        lab_coordaddress = CoordAddress.translate(lab_coordaddress_str)
        self._confirm_handler = self._confirm_experiment(lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data, resource_type_name)
        self._confirm_handler.join(self._enqueuing_timeout)

    @threaded(_resource_manager)
    @logged()
    def _confirm_experiment(self, lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data, resource_type_name):
        try:
            initial_time = datetime.datetime.now()
            try:
                labserver = self.locator[lab_coordaddress]
                reservation_result  = labserver.reserve_experiment(experiment_instance_id, client_initial_data, server_initial_data)
                lab_session_id, server_initialization_response, exp_info = reservation_result
            except Exception as e:
                if DEBUG:
                    traceback.print_exc()
                log.log( ReservationConfirmer, log.level.Error, "Exception confirming experiment: %s" % e )
                log.log_exc( ReservationConfirmer, log.level.Warning )

                self.coordinator.mark_experiment_as_broken(experiment_instance_id, [str(e)])
            else:
                end_time = datetime.datetime.now()
                experiment_coordaddress = CoordAddress.translate(exp_info['address'])
                self.coordinator.confirm_experiment(experiment_coordaddress, experiment_instance_id.to_experiment_id(), reservation_id, lab_coordaddress.address, lab_session_id, server_initialization_response, initial_time, end_time, resource_type_name, exp_info)
        except:
            if DEBUG:
                traceback.print_exc()
            log.log(ReservationConfirmer, log.level.Critical, "Unexpected exception confirming experiment")
            log.log_exc(ReservationConfirmer, log.level.Critical)

    @logged()
    def enqueue_free_experiment(self, lab_coordaddress_str, reservation_id, lab_session_id, experiment_instance_id):
        # We can stablish a policy such as using
        # thread pools or a queue of threads or something
        # like that... here
        if lab_session_id is None: # If the user didn't manage to obtain a session_id, don't call the free_experiment method
            experiment_response = None
            initial_time = end_time = datetime.datetime.now()
            self.coordinator.confirm_resource_disposal(lab_coordaddress_str, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time)
        else: # Otherwise...
            lab_coordaddress = CoordAddress.translate(lab_coordaddress_str)
            self._free_handler = self._free_experiment(lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id)
            self._free_handler.join(self._enqueuing_timeout)


    @threaded(_resource_manager)
    @logged()
    def _free_experiment(self, lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id):
        try:
            initial_time = datetime.datetime.now()
            try:
                labserver = self.locator[lab_coordaddress]
                experiment_response = labserver.free_experiment(SessionId.SessionId(lab_session_id))
            except Exception as e:
                if DEBUG:
                    traceback.print_exc()
                log.log( ReservationConfirmer, log.level.Error, "Exception freeing experiment: %s" % e )
                log.log_exc( ReservationConfirmer, log.level.Warning )

                self.coordinator.mark_experiment_as_broken(experiment_instance_id, [str(e)])
            else: # Everything went fine
                end_time = datetime.datetime.now()
                self.coordinator.confirm_resource_disposal(lab_coordaddress.address, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time)
        except:
            if DEBUG:
                traceback.print_exc()
            log.log(ReservationConfirmer, log.level.Critical, "Unexpected exception freeing experiment")
            log.log_exc(ReservationConfirmer, log.level.Critical)


    def enqueue_should_finish(self, lab_coordaddress_str, lab_session_id, reservation_id):
        lab_coordaddress = CoordAddress.translate(lab_coordaddress_str)
        self._should_finish(lab_coordaddress, lab_session_id, reservation_id)

    @threaded(_resource_manager)
    @logged()
    def _should_finish(self, lab_coordaddress, lab_session_id, reservation_id):
        try:
            try:
                labserver = self.locator[lab_coordaddress]
                received_experiment_response = labserver.should_experiment_finish(lab_session_id)
                experiment_response = float(received_experiment_response)
            except Exception as e:
                if DEBUG:
                    traceback.print_exc()
                log.log( ReservationConfirmer, log.level.Error, "Exception checking if the experiment should finish: %s" % e )
                log.log_exc( ReservationConfirmer, log.level.Warning )
                self.coordinator.confirm_should_finish(lab_coordaddress.address, lab_session_id, reservation_id, 0) # Don't try again with this reservation
            else:
                self.coordinator.confirm_should_finish(lab_coordaddress.address, lab_session_id, reservation_id, experiment_response)
        except:
            if DEBUG:
                traceback.print_exc()
            log.log(ReservationConfirmer, log.level.Critical, "Unexpected exception checking should_finish")
            log.log_exc(ReservationConfirmer, log.level.Critical)

