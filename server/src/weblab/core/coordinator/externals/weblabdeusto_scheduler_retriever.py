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
import weblab

from voodoo.counter import next_name

from weblab.core.coordinator.externals.weblabdeusto_scheduler_model import ExternalWebLabDeustoReservation

class ResultsRetriever(threading.Thread):
    def __init__(self, session_maker, resource_type_name, period):
        threading.Thread.__init__(self)
        self.setName(next_name("ResultsRetriever"))
        self.session_maker      = session_maker
        self.resource_type_name = resource_type_name
        self.period             = period
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

            self._process()

    def _process(self):
        pass

