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

import Queue

class TemporalInformationStore(object):
    """ Temporal synchronized store for batch and finishing information.

    The coordinator will be asking the experiment whether it has finished or not.
    Given that this process is not synchronized with the UserProcessingManager, not 
    even with the user session (if an experiment takes a long time and the user 
    session has finished, we still want to store the results of that experiment).
    Therefore, this store will store the information. From time to time, the 
    UserProcessingManager will call this store to ask for information to store in
    the database. This class provides synchronized solution, so the UPS will be 
    able to get blocked until some information is available.
    """
    def __init__(self):
        self.queue = Queue.Queue()

    def get(self, timeout = 0.5):
        """Get the first introduced object, waiting timeout time.

        Given that the same thread calls more than one store, the timeout should be quite small.
        """
        try:
            return self.queue.get(True, timeout)
        except Queue.Empty:
            return None

    def put(self, obj):
        self.queue.put(obj, False)

