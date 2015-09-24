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

from abc import ABCMeta, abstractmethod
import Queue
from voodoo.representable import Representable

class TemporalInformationStore(object):
    """ Temporal synchronized store for initial and finishing information.

    The coordinator will be asking the experiment whether it has finished or not.
    Given that this process is not synchronized with the UserProcessingManager, not
    even with the user session (if an experiment takes a long time and the user
    session has finished, we still want to store the results of that experiment).
    Therefore, this store will store the information. From time to time, the
    UserProcessingManager will call this store to ask for information to store in
    the database. This class provides synchronized solution, so the UPS will be
    able to get blocked until some information is available.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.queue = Queue.Queue()

    def get(self, timeout = None):
        """Get the first introduced object, waiting timeout time.

        Given that the same thread calls more than one store, the timeout should be quite small.
        """
        if timeout is None:
            real_timeout = 0.05
        else:
            real_timeout = timeout
        try:
            return self.queue.get(True, real_timeout)
        except Queue.Empty:
            return None

    def empty(self):
        return self.queue.empty()

    @abstractmethod
    def put(self, *args, **kwargs):
        pass

class InitialInformationEntry(object):
    
    __metaclass__ = Representable

    def __init__(self, reservation_id, experiment_id, exp_coordaddr, initial_configuration, initial_time, end_time, request_info, client_initial_data):
        self.reservation_id        = reservation_id
        self.experiment_id         = experiment_id
        self.exp_coordaddr         = exp_coordaddr
        self.initial_configuration = initial_configuration
        self.initial_time          = initial_time
        self.end_time              = end_time
        self.request_info          = request_info
        self.client_initial_data   = client_initial_data

class InitialTemporalInformationStore(TemporalInformationStore):
    def put(self, initial_information_entry):
        self.queue.put_nowait(initial_information_entry)

class FinishTemporalInformationStore(TemporalInformationStore):
    def put(self, reservation_id, obj, initial_time, end_time):
        self.queue.put_nowait((reservation_id, obj, initial_time, end_time))

class CommandOrFileInformationEntry(object):
    
    __metaclass__ = Representable

    def __init__(self, reservation_id, is_before, is_command, entry_id, payload, timestamp):
        self.reservation_id  = reservation_id
        self.is_before       = is_before  # or after
        self.is_command      = is_command # or file
        self.entry_id        = entry_id # random number identifying the entry
        self.payload         = payload
        self.timestamp       = timestamp

class CommandsTemporalInformationStore(TemporalInformationStore):
    def put(self, command_information_entry):
        self.queue.put_nowait(command_information_entry)

class CompletedInformationStore(TemporalInformationStore):
    def put(self, username, usage, callback):
        self.queue.put_nowait((username, usage, callback))

