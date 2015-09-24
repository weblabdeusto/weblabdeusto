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

import random
import json

from voodoo.override import Override
import voodoo.log as log

import weblab.core.coordinator.status as WSS
from weblab.core.coordinator.scheduler import Scheduler
from weblab.core.coordinator.clients.ilab_batch import iLabBatchLabServerProxy
from weblab.core.coordinator.sql.externals.ilab_batch_scheduler_model import ILabBatchReservation
from voodoo.log import logged

class ILabBatchScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, lab_server_url, identifier, passkey, **kwargs):
        super(ILabBatchScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

        self.lab_server_url   = lab_server_url
        self.identifier       = identifier
        self.passkey          = passkey

    def stop(self):
        pass

    @Override(Scheduler)
    def is_remote(self):
        return True

    @logged()
    @Override(Scheduler)
    def removing_current_resource_slot(self, session, resource_instance_id):
        # Will in fact never be called
        return False

    def _create_client(self):
        return iLabBatchLabServerProxy(self.lab_server_url, self.identifier, self.passkey)

    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data, request_info):
        if not 'operation' in client_initial_data:
            raise Exception("Invalid client_initial_data. If you are using iLab, you should reserve it through /weblab/web/ilab/, or use the same scheme")

        client = self._create_client()
        if client_initial_data['operation'] == 'get_lab_configuration':
            config = client.get_lab_configuration()
            return WSS.PostReservationStatus(reservation_id, True, config, '')
        elif client_initial_data['operation'] == 'submit':
            # TODO!!!
            remote_experiment_id  = random.randint(1000000, 200000000)
            session = self.session_maker()
            try:
                reservation = ILabBatchReservation(reservation_id, self.lab_server_url, remote_experiment_id)
                session.add(reservation)
                session.commit()
            finally:
                session.close()

            # submit(self, experiment_id, experiment_specification, user_group, priority_hint)
            experiment_specification = client_initial_data['payload']
            accepted, warnings, error, est_runtime, lab_exp_id, min_time_to_live, queue_length, wait = client.submit( remote_experiment_id , experiment_specification, "weblab-deusto", 0)
            # TODO: do something with the arguments :-)
            return WSS.WaitingQueueStatus(reservation_id, queue_length)
        else:
            raise Exception("Invalid operation in client_initial_data")

    #######################################################################
    #
    # Given a reservation_id, it returns in which state the reservation is
    #
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        session = self.session_maker()
        try:
            reservation = session.query(ILabBatchReservation).filter_by(local_reservation_id = reservation_id, lab_server_url = self.lab_server_url).first()
            if reservation is None:
                # TODO
                raise Exception("reservation not stored in local database")

            remote_experiment_id = reservation.remote_experiment_id
        finally:
            session.close()

        #     public class StorageStatus
        # public const int BATCH_QUEUED = 1; // if waiting in the execution queue
        # public const int BATCH_RUNNING = 2; //if currently running
        # public const int BATCH_TERMINATED = 3; // if terminated normally
        # public const int BATCH_TERMINATED_ERROR = 4; // if terminated with errors (this includes cancellation by user in mid-execution)
        # public const int BATCH_CANCELLED = 5; // if cancelled by user before execution had begun
        # public const int BATCH_UNKNOWN = 6; // if unknown labExperimentID.
        # public const int BATCH_NOT_VALID = 7; // Assigned by Service Broker if experiment is not valid (done in submit call)

        client = self._create_client()
        code, queue_length, est_wait, est_rt, est_rem_rt, min_to_live = client.get_experiment_status(remote_experiment_id)
        # TODO do something with the rest of the variables
        if code == 1:
            return WSS.WaitingQueueStatus(reservation_id, queue_length)
        elif code == 2:
            return WSS.WaitingConfirmationQueueStatus(reservation_id, self.core_server_url)
        elif code == 3:
             code, results, xmlResultExtension, xmlBlobExtension, warnings, error = client.retrieve_result(remote_experiment_id)
             response = json.dumps({
                'code'    : code,
                'results' : results,
                'xmlResults' : xmlResultExtension,
             })
             return WSS.PostReservationStatus(reservation_id, True, response, '')
        else:
            return WSS.PostReservationStatus(reservation_id, True, "ERROR: WebLab-Deusto can't handle status code %s at this point" % code, '')



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
        session = self.session_maker()
        try:
            reservation = session.query(ILabBatchReservation).filter_by(local_reservation_id = reservation_id, lab_server_url = self.lab_server_url).first()
            if reservation is not None:
                remote_experiment_id = reservation.remote_experiment_id
                session.delete(reservation)
                session.commit()
            else:
                return
        finally:
            session.close()

        client = self._create_client()
        try:
            client.cancel(remote_experiment_id)
        except:
            log.log(ILabBatchScheduler, log.level.Error, "Skipping error when cancelling iLab reservation")
            log.log_exc(ILabBatchScheduler, log.level.Error)

    ##############################################################
    #
    # ONLY FOR TESTING: It completely removes the whole database
    #
    @Override(Scheduler)
    def _clean(self):
        session = self.session_maker()

        try:
            for reservation in session.query(ILabBatchReservation).all():
                session.delete(reservation)
            session.commit()
        finally:
            session.close()


