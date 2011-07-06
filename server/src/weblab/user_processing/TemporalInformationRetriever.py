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

        self.keep = True
        self.batch_store    = batch_store
        self.finished_store = finished_store

    def run(self):
        while self.keep:
            try:
                self.iterate()
            except:
                log.log( TemporalInformationRetriever, log.LogLevel.Critical, "Exception iterating in TemporalInformationRetriever!!!")
                log.log_exc( TemporalInformationRetriever, log.LogLevel.Critical )

    def stop(self):
        self.keep = False

    def iterate(self):
        pass
