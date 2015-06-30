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

import cPickle as pickle
import threading
import time
import numbers
import urllib2
import json

import voodoo.log as log
from voodoo.counter import next_name
from voodoo.sessions.session_id import SessionId

from weblab.data.experiments import ExperimentId

class ResultsRetriever(threading.Thread):
    def __init__(self, weblabdeusto_scheduler, period, create_client_func):
        threading.Thread.__init__(self)
        self.setName(next_name("ResultsRetriever"))
        self.redis_maker        = weblabdeusto_scheduler.redis_maker
        self.resource_type_name = weblabdeusto_scheduler.resource_type_name
        self.server_route       = weblabdeusto_scheduler.core_server_route
        self.server_url         = weblabdeusto_scheduler.core_server_url # Not required, but helpful for debugging
        self.completed_store    = weblabdeusto_scheduler.completed_store
        self.post_reservation_data_manager = weblabdeusto_scheduler.post_reservation_data_manager
        self.period             = period
        self.create_client_func = create_client_func
        self.stopped            = False

        self.external_weblabdeusto_pending = weblabdeusto_scheduler.EXTERNAL_WEBLABDEUSTO_PENDING_RESULTS % (self.resource_type_name, self.server_route)

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
        redis_client = self.redis_maker()
        pending_results = []
        for reservation_id in redis_client.hkeys(self.external_weblabdeusto_pending):
            pending_result_str = redis_client.hget(self.external_weblabdeusto_pending, reservation_id)
            if pending_result_str is not None:
                pending_result = json.loads(pending_result_str)
                pending_result['reservation_id'] = reservation_id
                pending_results.append(pending_result)

        if len(pending_results) > 0:
            try:
                session_id, client = self.create_client_func(None)
            except urllib2.URLError:
                # Remote server is down, try later
                return

            remote_reservation_ids = [ SessionId(pending_result['remote_reservation_id']) for pending_result in pending_results ]

            results = client.get_experiment_uses_by_id(session_id, remote_reservation_ids)

            for pending_result, result in zip(pending_results, results):
                if result.is_alive():
                    continue

                username      = pending_result['username']
                try:
                    request_info  = pickle.loads(pending_result['serialized_request_info'].encode('utf-8'))
                except Exception as e:
                    log.log(ResultsRetriever, log.level.Critical, "Probably serialized_request_info was truncated in %s" % pending_result)
                    log.log_exc(ResultsRetriever, log.level.Error)
                    request_info  = {'error' : 'could not be stored: %s' % e}
                reservation_id = pending_result['reservation_id']
                remote_reservation_id = pending_result['remote_reservation_id']

                if not redis_client.hdel(self.external_weblabdeusto_pending, reservation_id):
                    log.log(ResultsRetriever, log.level.Info, "Pending reservation %r not found. Assuming it is managed by other thread" % pending_result)
                    continue

                if result.is_finished():
                    use = result.experiment_use
                    use.experiment_id = ExperimentId.parse(pending_result['experiment_id_str'])
                    use.remote_reservation_id = remote_reservation_id
                    use.reservation_id = reservation_id

                    for key in [ key for key in request_info ]:
                        if not isinstance(request_info[key], (basestring, numbers.Number)):
                            request_info.pop(key)
                    use.request_info   = request_info
                    callback = lambda : self.post_reservation_data_manager.delete(reservation_id)
                    self.completed_store.put(username, use, callback)
                else:
                    log.log(ResultsRetriever, log.level.Info, "Reservation id %s was cancelled and therefore not stored" % reservation_id)

