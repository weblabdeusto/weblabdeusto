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

import voodoo.log as log

class TemporalInformationRetriever(threading.Thread):
    """
    This class retrieves continuously the information of batch and finished experiments.
    """

    def __init__(self, batch_store, finished_store):
        threading.Thread.__init__(self)

        self.keep_running = True
        self.batch_store    = batch_store
        self.finished_store = finished_store
        self.timeout        = None

    def run(self):
        while self.keep_running:
            try:
                self.iterate()
            except:
                log.log( TemporalInformationRetriever, log.LogLevel.Critical, "Exception iterating in TemporalInformationRetriever!!!")
                log.log_exc( TemporalInformationRetriever, log.LogLevel.Critical )

    def stop(self):
        self.keep_running = False

    def iterate(self):
        self.iterate_over_store(self.batch_store)
        if self.keep_running:
            self.iterate_over_store(self.finished_store)

    def iterate_over_store(self, store):
        information = store.get(timeout=self.timeout)
        if information is not None:
            reservation_id, obj = information
            print reservation_id, obj
            

