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

import StringIO
import traceback
import threading

import voodoo.log as log
import voodoo.counter as counter

class _ThreadedFunc(threading.Thread):
    def __init__(self, func, otherself, args, kargs, resource_manager, logging):
        super(_ThreadedFunc,self).__init__(name = counter.next_name("_ThreadedFunc_for_" + func.__name__))
        self._self             = otherself
        self._args             = args
        self._kargs            = kargs
        self._func             = func
        self._resource_manager = resource_manager

        self.result            = None
        self.raised_exc        = None
        self.finished_ok       = False
        self.logging           = logging

        if self._resource_manager != None:
            self._resource_manager.add_resource(self)

    def run(self):
        try:
            try:
                self.result = self._func(
                    self._self,
                    *self._args,
                    **self._kargs
                )
                self.finished_ok = True
            finally:
                if self._resource_manager != None:
                    self._resource_manager.remove_resource(self)
        except Exception as e:
            self.raised_exc = e
            if self.logging:
                log.log(
                    _ThreadedFunc,
                    log.level.Warning,
                    "threaded: exception caught while running %s: %s" % (
                            self._func.__name__,
                            e
                        )
                )
                log.log_exc( _ThreadedFunc, log.level.Warning)

            sio = StringIO.StringIO()
            traceback.print_exc(file=sio)
            self.raised_exc_traceback = sio.getvalue()

# This is used at most once per threaded method is created
_global_threaded_thread = threading.Lock()

def threaded(resource_manager = None, logging = True):
    """
    threaded is a decorator that launches functions in new threads.

    @threaded()
    def foo(self, param1, param2):
        # This code will be executed in a new thread

    handler = foo(1,2)
    #handler is _ThreadedFunc
    handler.join()
    if handler.finished_ok:
        print "Result is %s" % handler.result
    else:
        print "Exception raised: %s" % handler.raised_exc

    threaded has an optional argument which is a voodoo.resources_manager.ResourceManager

    It seems to be quite similar to Join Java asynchronous methods:
    http://en.wikipedia.org/wiki/Join_Java#Asynchronous_methods
    """
    def wrapped_threaded(func):
        def auxiliar_func(self, threaded_func):
            self._threaded_threads_lock.acquire()
            try:
                self._threaded_threads = [ i for i in self._threaded_threads if i.isAlive() ]
                self._threaded_threads.append(threaded_func)
            finally:
                self._threaded_threads_lock.release()

        def wrapped_func(self, *args, **kargs):
            threaded_func = _ThreadedFunc(func,self,args,kargs, resource_manager, logging)
            if hasattr(self,"_threaded_threads_lock"):
                auxiliar_func(self, threaded_func)
            else:
                _global_threaded_thread.acquire()
                try:
                    # Check now again (if two threads enter at the same time,
                    # it might be a problem)
                    if hasattr(self, "_threaded_threads_lock"):
                        auxiliar_func(self,threaded_func)
                    else:
                        self._threaded_threads_lock = threading.Lock()
                        self._threaded_threads_lock.acquire()
                        try:
                            self._threaded_threads = [threaded_func]
                        finally:
                            self._threaded_threads_lock.release()
                finally:
                    _global_threaded_thread.release()

            threaded_func.start()
            return threaded_func

        wrapped_func.__doc__  = func.__doc__
        wrapped_func.__name__ = func.__name__
        return wrapped_func

    return wrapped_threaded

