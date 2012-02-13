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

import threading
import time
import urllib2

import voodoo.log as log
from voodoo.counter import next_name
from voodoo.sessions.session_id import SessionId

from weblab.core.coordinator.externals.weblabdeusto_scheduler_model import ExternalWebLabDeustoReservationPendingResults

class ResultsRetriever(threading.Thread):
    def __init__(self, session_maker, resource_type_name, server_route, period, create_client_func):
        threading.Thread.__init__(self)
        self.setName(next_name("ResultsRetriever"))
        self.session_maker      = session_maker
        self.resource_type_name = resource_type_name
        self.period             = period
        self.server_route       = server_route
        self.create_client_func = create_client_func
        self.stopped            = False

    def stop(self):
        self.stopped = True
        self.join()

    def run(self):
        while not self.stopped:

            amount = 0.0
            while not self.stopped and amount < self.period:
                timestep = 0.01
                time.sleep(timestep)
                amount += timestep

            if self.stopped:
                break

            try:
                self._process()
            except:
                import traceback
                traceback.print_exc()
                log.log(ResultsRetriever, log.level.Critical, "Unexpected error retrieving results from remote server. Retrying in %s seconds" % self.period)
                log.log_exc(ResultsRetriever, log.level.Error)

    def _process(self):
        session = self.session_maker()
        try:
            pending_results = session.query(ExternalWebLabDeustoReservationPendingResults).filter_by(resource_type_name = self.resource_type_name, server_route = self.server_route).all()
        finally:
            session.close()

        if len(pending_results) > 0:
            try:
                session_id, client = self.create_client_func(None)
            except urllib2.URLError:
                # Remote server is down, try later
                return

            remote_reservation_ids = [ SessionId(pending_result.remote_reservation_id) for pending_result in pending_results ]

            results = client.get_experiment_uses_by_id(session_id, remote_reservation_ids)
            for pending_result, result in zip(pending_results, results):
                # print result
                pass

