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

import cPickle as pickle
from voodoo.override import Override
from weblab.core.coordinator.scheduler import Scheduler
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.core.coordinator.externals.weblabdeusto_scheduler_model import ExternalWebLabDeustoReservation
from voodoo.log import logged

class ExternalWebLabDeustoScheduler(Scheduler):

    def __init__(self, generic_scheduler_arguments, baseurl, username, password, **kwargs):
        super(ExternalWebLabDeustoScheduler, self).__init__(generic_scheduler_arguments, **kwargs)

        self.baseurl  = baseurl
        self.username = username
        self.password = password

    def stop(self):
        pass

    @logged()
    @Override(Scheduler)
    def removing_current_resource_slot(self, session, resource_instance_id):
        # Will in fact never be called
        return False

    # TODO: pooling
    def _create_client(self, cookies = None):
        client = WebLabDeustoClient(self.baseurl)
        if cookies is not None:
            client.setcookies(cookies)
        return client

    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    @logged()
    @Override(Scheduler)
    def reserve_experiment(self, reservation_id, experiment_id, time, priority, initialization_in_accounting, client_initial_data):

        consumer_data = {
            'time_allowed'                 : time,
            'priority'                     : priority,
            'initialization_in_accounting' : initialization_in_accounting
        }

        client = self._create_client()
        session_id = self.client.login(self.username,self.password)
        reservation_status = client.reserve_experiment(session_id, experiment_id, client_initial_data, consumer_data)

        cookies = client.get_cookies()
        serialized_cookies = pickle.dumps(cookies)

        session = self.sessionmaker()
        try:
            reservation = ExternalWebLabDeustoReservation(reservation_id, reservation_status.reservation_id, serialized_cookies, time.time())
            session.add(reservation)
            session.commit()
        finally:
            session.close()

        reservation_status.reservation_id = reservation_id

        return reservation_status 

    #######################################################################
    # 
    # Given a reservation_id, it returns in which state the reservation is
    # 
    @logged()
    @Override(Scheduler)
    def get_reservation_status(self, reservation_id):
        
        session = self.sessionmaker()
        try:
            reservation = session.query(ExternalWebLabDeustoReservation).filter_by(local_reservation_id = reservation_id).first()
            if reservation is None:
                # TODO
                raise Exception("reservation not stored in local database")

            remote_reservation_id = reservation.remote_reservation_id
            serialized_cookies    = reservation.cookies
        finally:
            session.close()
        
        cookies = pickle.loads(serialized_cookies)
        client = self._create_client(cookies)

        reservation_status = client.get_reservation_status(remote_reservation_id)

        reservation_status.reservation_id = reservation_id

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
            reservation = session.query(ExternalWebLabDeustoReservation).filter_by(local_reservation_id = reservation_id).first()
            if reservation is not None:
                remote_reservation_id = reservation.remote_reservation_id
                serialized_cookies = reservation.cookies
                session.delete(reservation)
                session.commit()
            else:
                return
        finally:
            session.close()

        cookies = pickle.loads(serialized_cookies)
        client = self._create_client(cookies)
        client.finished_experiment(remote_reservation_id)

    ##############################################################
    # 
    # ONLY FOR TESTING: It completely removes the whole database
    # 
    @Override(Scheduler)
    def _clean(self):
        session = self.session_maker()

        try:
            for reservation in session.query(ExternalWebLabDeustoReservation).all():
                session.delete(reservation)
            session.commit()
        finally:
            session.close()


