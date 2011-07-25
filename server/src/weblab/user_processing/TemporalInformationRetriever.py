#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import voodoo.log as log

import weblab.data.experiments.Usage as Usage
import weblab.data.Command as Command

class TemporalInformationRetriever(threading.Thread):
    """
    This class retrieves continuously the information of initial and finished experiments.
    """

    def __init__(self, initial_store, finished_store, db_manager):
        threading.Thread.__init__(self)

        self.keep_running = True
        self.initial_store    = initial_store
        self.finished_store = finished_store
        self.iterations     = 0
        self.db_manager     = db_manager
        self.timeout        = None
        self.setDaemon(True)

    def run(self):
        while self.keep_running:
            try:
                self.iterations += 1
                self.iterate()
            except:
                log.log( TemporalInformationRetriever, log.LogLevel.Critical, "Exception iterating in TemporalInformationRetriever!!!")
                log.log_exc( TemporalInformationRetriever, log.LogLevel.Critical )

    def stop(self):
        self.keep_running = False

    def iterate(self):
        self.iterate_over_store(self.initial_store, 'initial')
        if self.keep_running:
            self.iterate_over_store(self.finished_store, 'finish')

    def iterate_over_store(self, store, message):
        information = store.get(timeout=self.timeout)
        if information is not None:
            reservation_id, obj = information

            command = Usage.CommandSent(
                    Command.Command("@@@%s@@@" % message), time.time(),
                    Command.Command(str(obj)), time.time()
            )

            if not self.keep_running or not self.db_manager.append_command(reservation_id, command):
                # If it could not be added because the experiment id
                # did not exist, put it again in the queue
                store.put(reservation_id, obj)

