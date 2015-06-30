#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import time
import random
import Queue
import threading

import voodoo.log as log
import voodoo.resources_manager as ResourceManager
import voodoo.counter as counter
from voodoo.resources_manager import is_testing

_resource_manager = ResourceManager.CancelAndJoinResourceManager("UserProcessingServer")

############################################################
#
# Certain operations, such as updating the queues, we
# only want them to be executed by one thread at a time.
# We can execute them more often, but it simply does not
# make sense. This class provides one public method, called
# request_and_wait. The method makes sure that the update
# method of the scheduler is called once since the method
# is invoked, without mattering if somebody else requested
# it.
#
class SchedulerTransactionsSynchronizer(threading.Thread):
    def __init__(self, scheduler, min_time_between_updates = 0.0, max_time_between_updates = 0.0):
        super(SchedulerTransactionsSynchronizer, self).__init__()
        self.setName(counter.next_name("SchedulerTransactionsSynchronizer"))
        self.setDaemon(True)
        self.scheduler = scheduler
        self.queue = Queue.Queue()
        self.stopped = False

        self.pending_elements = []
        self.pending_elements_condition = threading.Condition()

        self._latest_update = 0 # epoch
        self.period_lock = threading.Lock()
        self.min_time_between_updates = int(min_time_between_updates * 1000)
        self.max_time_between_updates = int(max_time_between_updates * 1000)
        self.next_period_between_updates = 0


    def _update_period_between_updates(self):
        self.next_period_between_updates = random.randint(self.min_time_between_updates, self.max_time_between_updates) / 1000.0

    def start(self):
        super(SchedulerTransactionsSynchronizer, self).start()
        _resource_manager.add_resource(self)

    def stop(self):
        self.stopped = True
        self.join()
        _resource_manager.remove_resource(self)

    def cancel(self):
        self.stop()

    def run(self):
        timeout = 0.2
        if is_testing():
            timeout = 0.01
        while not self.stopped:
            try:
                element = self.queue.get(timeout=timeout)
            except Queue.Empty:
                continue

            if element is not None:
                self._iterate(element)


    def _iterate(self, element):
        elements = [element]
        while True:
            try:
                new_element = self.queue.get_nowait()
                elements.append(new_element)
            except Queue.Empty:
                break

        if not self.stopped:
            execute = True
            with self.period_lock:
                if time.time() - self._latest_update <= self.next_period_between_updates:
                    execute = False
                else:
                    self._latest_update = time.time()
                    self._update_period_between_updates()

            if execute:
                try:
                    self.scheduler.update()
                except:
                    log.log(SchedulerTransactionsSynchronizer, log.level.Critical, "Exception updating scheduler")
                    log.log_exc(SchedulerTransactionsSynchronizer, log.level.Critical)


        self._notify_elements(elements)


    def _notify_elements(self, elements):

        with self.pending_elements_condition:
            for element in elements:
                if element in self.pending_elements:
                    self.pending_elements.remove(element)

            self.pending_elements_condition.notify_all()

    def request_and_wait(self):
        request_id = "%s::%s" % (threading.current_thread().getName(), random.random())

        with self.pending_elements_condition:
            self.pending_elements.append(request_id)


        self.queue.put_nowait(request_id)


        with self.pending_elements_condition:
            while request_id in self.pending_elements and self.isAlive():
                self.pending_elements_condition.wait(timeout=5)


