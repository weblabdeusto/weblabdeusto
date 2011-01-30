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
import weakref
import voodoo.LogLevel as LogLevel
import voodoo.log as log

def sleep(t): # For testing purposes
    time.sleep(t)

class ResourcesCheckerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.frequency   = None # Seconds
        self.coordinator = None

    def run(self):
        while True:
            try:
                sleep(1)
                if self.frequency is None:
                    continue
                # Here self.frequency is configured, so wait the rest of the required time
                if self.frequency > 1:
                    sleep(self.frequency - 1)

                coordinator = self.coordinator()
                if coordinator is None:
                    continue # coordinator not configured yet

            except Exception, e:
                log.log(ResourcesCheckerThread, LogLevel.Error,
                    "Exception checking resources: %s" % e )
                log.log_exc(ResourcesCheckerThread, LogLevel.Error)

checker_thread = ResourcesCheckerThread()
checker_thread.setDaemon(True)
checker_thread.start()

def set_coordinator(coordinator, new_frequency):
    checker_thread.frequency   = new_frequency
    checker_thread.coordinator = weakref.ref(coordinator)

