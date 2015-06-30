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

import threading
import time

NUM=0

def locked(lock_name = '_lock'):
    def locked_with_name(func):
        def wrapped_locked(self,*args, **kargs):
            the_lock = getattr(self,lock_name)
#           global NUM
#           print "Acquiring...",func,NUM
            the_lock.acquire()
#           NUM += 1
#           print "\tAcquired",func
            try:
                return func(self,*args, **kargs)
            finally:
#               NUM -= 1
#               print "Releasing...",func, NUM
                the_lock.release()
        wrapped_locked.__name__ = func.__name__
        wrapped_locked.__doc__  = func.__doc__
        return wrapped_locked
    return locked_with_name

class UnfairLock(object):
    # This is far better than 0.01 or 0.0001, but I haven't tried other values.
    # Of course, this value depends much on the computer
    SLICE = 0.001
    def __init__(self):
        self._lock = threading.Lock()

    def acquire(self):
        while True:
            acquired = self._lock.acquire(False)
            if acquired:
                return
            time.sleep(self.SLICE)

    def release(self):
        self._lock.release()

class _InternalReadLock(object):
    def __init__(self, rwlock):
        self.rwlock = rwlock

    def acquire(self):
        self.rwlock._acquire_reading()

    def release(self):
        self.rwlock._release_reading()

class _InternalWriteLock(object):
    def __init__(self, rwlock):
        self.rwlock = rwlock

    def acquire(self):
        self.rwlock._acquire_writing()

    def release(self):
        self.rwlock._release_writing()

class RWLock(object):
    _SHORT_TIME = 0.05
    def __init__(self):
        self._lock = threading.RLock()

        self._read_lock  = _InternalReadLock(self)
        self._write_lock = _InternalWriteLock(self)

        self._condition = threading.Condition()

        self._reading = 0
        self._writing = None

    @locked()
    def _get_reading(self):
        return self._reading

    @locked()
    def _increment_reading(self):
        self._reading += 1

    @locked()
    def _decrement_reading(self):
        self._reading -= 1

    @locked()
    def _set_writing(self):
        self._writing = [threading.currentThread(), 1]

    @locked()
    def _decrement_writing(self):
        self._writing[1] = self._writing[1] - 1
        if self._writing[1] == 0:
            self._writing = None

    @locked()
    def _is_writing(self):
        return self._writing != None

    @locked()
    def _someone_else_is_writing(self):
        return self._writing != None and self._writing[0] != threading.currentThread()

    @locked()
    def _am_i_writing(self):
        am_i = self._writing != None and self._writing[0] == threading.currentThread()
        if am_i:
            self._writing[1] = self._writing[1] + 1
        return am_i

    def _acquire_reading(self):
        self._condition.acquire()
        try:
            while self._someone_else_is_writing():
                self._condition.wait()

            self._increment_reading()

            self._condition.notifyAll()
        finally:
            self._condition.release()

    def _acquire_writing(self):
        self._condition.acquire()
        try:
            if not self._am_i_writing():

                while self._get_reading() > 0 or self._is_writing():
                    self._condition.wait()

                self._set_writing()

            self._condition.notifyAll()
        finally:
            self._condition.release()

    def _release_reading(self):
        self._condition.acquire()
        try:
            self._decrement_reading()

            self._condition.notifyAll()
        finally:
            self._condition.release()

    def _release_writing(self):
        self._condition.acquire()
        try:
            self._decrement_writing()

            self._condition.notifyAll()
        finally:
            self._condition.release()

    def read_lock(self):
        return self._read_lock

    def write_lock(self):
        return self._write_lock

