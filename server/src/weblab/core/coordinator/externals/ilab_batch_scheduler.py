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

import time as time_mod
import cPickle as pickle
import json

from voodoo.override import Override
from voodoo.sessions.session_id import SessionId

from weblab.core.user_processor import FORWARDED_KEYS, SERVER_UUIDS
import weblab.core.coordinator.status as WSS
from weblab.core.coordinator.scheduler import Scheduler
from weblab.core.coordinator.clients.ilab_batch import iLabBatchLabServerProxy
from weblab.core.coordinator.externals.ilab_batch_scheduler_model import ILabBatchReservation
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
    
        if client_initial_data['operation'] == 'get_lab_configuration':
           client = self._create_client()
           config = client.get_lab_configuration()
           return WSS.PostReservationStatus(reservation_id, True, config, '')
           
        raise Exception("SHOULD NOT ACHIEVE THIS POINT")

    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        raise Exception("SHOULD NOT ACHIEVE THIS POINT (2)")

        session = self.session_maker()
        try:
            reservation = session.query(ILabBatchReservation).filter_by(local_reservation_id = reservation_id, lab_server_url = self.lab_sever_url).first()
            if reservation is None:
                # TODO
                raise Exception("reservation not stored in local database")

            remote_reservation_id = reservation.remote_reservation_id
            serialized_cookies    = reservation.cookies
        finally:
            session.close()
        
        cookies = pickle.loads(str(serialized_cookies))
        client = self._create_client(cookies)

        reservation = client.get_reservation_status(SessionId(remote_reservation_id))

        return self._convert_reservation_to_status(reservation, reservation_id, remote_reservation_id)

    def _convert_reservation_to_status(self, reservation, local_reservation_id, remote_reservation_id):
        reservation_status = reservation.to_status()
        reservation_status.set_reservation_id(local_reservation_id)
        if reservation_status.status == WSS.WebLabSchedulingStatus.RESERVED_REMOTE and reservation_status.remote_reservation_id == '':
            reservation_status.set_remote_reservation_id(remote_reservation_id)

        return reservation_status
       


    ################################################################
    #
    # Called when it is confirmed by the Laboratory Server.
    #
    @logged()
    @Override(Scheduler)
    def confirm_experiment(self, reservation_id, lab_session_id, initial_configuration):
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
        client.cancel(remote_experiment_id)

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


