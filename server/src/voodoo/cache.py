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

import six.moves.cPickle as pickle

import weakref
import threading
import sys
import time as time_module

class _HasheableKey(object):
    """ If args are hasheable and there is no kwargs (which will
    never be hasheable), then there is no need to pickle anything, so
    everything will run far faster.
    """
    def __init__(self, args):
        self._args = args
    def load(self, dictionaries):
        dict_cache = dictionaries['dict']
        if self._args in dict_cache:
            return True, dict_cache[self._args]
        return False, (None,None)
    def save(self, dictionaries, value):
        obj, current_time = value
        dict_cache = dictionaries['dict']
        dict_cache[self._args] = (obj, current_time)
    def pop(self, dictionaries):
        dict_cache = dictionaries['dict']
        return dict_cache.pop(self._args)

class _PicklableKey(object):
    def __init__(self, pickled_key):
        self._pickled_key = pickled_key
    def load(self, dictionaries):
        dict_cache = dictionaries['dict']
        if self._pickled_key in dict_cache:
            return True,dict_cache[self._pickled_key]
        return False, (None,None)
    def save(self, dictionaries, value):
        obj, current_time = value
        dict_cache = dictionaries['dict']
        dict_cache[self._pickled_key] = (obj, current_time)
    def pop(self, dictionaries):
        dict_cache = dictionaries['dict']
        return dict_cache.pop(self._pickled_key)

class _NotPicklableKey(object):
    def __init__(self, key):
        self._key = key
    def load(self, dictionaries):
        list_cache = dictionaries['list']
        for real_key, obj in list_cache:
            if real_key == self._key:
                return True, obj
        return False, (None, None)
    def save(self, dictionaries, value):
        obj, current_time = value
        list_cache = dictionaries['list']
        found, old_obj = self.load(dictionaries)
        if not found:
            list_cache.append((self._key,(obj, current_time)))
    def pop(self, dictionaries):
        list_cache = dictionaries['list']
        for pos,(real_key, obj) in enumerate(list_cache):
            if real_key == self._key:
                return list_cache.pop(pos)[1]

_cache_registry = []
_fast_cache_registry = []

DEBUGGING = False

class _CacheCleaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("CacheCleaner")
        self.stopping = False

    def stop(self):
        self.stopping = True

    def clean_cache_obj(self, cache_obj):

        cache_time = cache_obj.time
        if cache_time is None:
            return

        current_time = time_module.time()
        for inst in cache_obj.dictionaries_per_inst:
            inst_dict = cache_obj.dictionaries_per_inst[inst]['dict']
            keys_to_remove = []
            for key in inst_dict:
                obj, storage_time = inst_dict[key]
                if current_time - storage_time > cache_time:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                inst_dict.pop(key)

            inst_list = cache_obj.dictionaries_per_inst[inst]['list']
            i = 0
            while i < len(inst_list):
                key, (obj, storage_time) = inst_list[i]
                if current_time - storage_time < cache_time:
                    inst_list.pop(i)
                else:
                    i += 1

    def clean_fast_cache_obj(self, fast_cache_obj):
        for keys in fast_cache_obj.cache.keys():
            if len(keys) > 0:
                if type(keys[0]) == weakref.ReferenceType:
                    if keys[0]() is None:
                        fast_cache_obj.pop(keys[0])

    def run(self):
        while not self.stopping:
            try:
                copy = _cache_registry[:]
                for cache_obj in copy:
                    self.clean_cache_obj(cache_obj)
                    time_module.sleep(1)
                copy = _fast_cache_registry[:]
                for fast_cache_obj in copy:
                    self.clean_fast_cache_obj(fast_cache_obj)
                    time_module.sleep(1)
                time_module.sleep(1)
            except Exception as e:
                if DEBUGGING:
                    print("Error!",e)
                    import traceback
                    traceback.print_exc()

_cache_cleaner = _CacheCleaner()
_cache_cleaner.setDaemon(True)
_cache_cleaner.start()

def cache(time_to_wait = None, resource_manager = None):
    """ cache(time in float seconds) -> decorator

    Given "time" seconds (float), this decorator will cache during that
    time the output of the decorated function. This way, if someone calls
    the cache object with the same input within the next "time" time, the
    function will not be called and the output will be returned instead.
    """
    class cache_obj(object):
        def __init__(self, func):
            super(cache_obj,self).__init__()
            self.func         = (func,)
            self.lock         = threading.RLock()
            self.dictionaries_per_inst = {
                    # inst : { # if it's not an inst, None is the key
                    #   'dict': {},
                    #   'list': []
                    # }
                 }
            self._time        = time_to_wait
            self._inst        = None
            _cache_registry.append(self)

        def __get__(self, inst, owner):
            if inst is not None:
                self._inst = weakref.ref(inst)
            return self

        def _generate_key(self, args, kargs):
            if kargs == {}:
                try:
                    hash(args)
                except TypeError:
                    pass
                else:
                    key = _HasheableKey(args)
                    return key
            try:
                pickled_key = pickle.dumps((args,kargs))
            except:
                key = _NotPicklableKey((args,kargs))
            else:
                key = _PicklableKey(pickled_key)
            return key

        def _get_time(self):
            # For testing purposes
            return time_module.time()

        def __call__(self, *args, **kargs):
            key = self._generate_key(args, kargs)
            current_time = self._get_time()

            found, (obj, storage_time) = key.load(self._get_dictionaries())
            if found:
                if self.time is None or current_time - storage_time < self.time:
                    return obj

            if self._inst != None:
                args = (self._inst(),) + args
            return_value = self.func[0](*args, **kargs)

            key.save(
                    self._get_dictionaries(),
                    ( return_value, current_time)
                )

            return return_value

        def _save_to_cache(self, key, value):
            return_value, current_time = value
            key.save(self._get_dictionaries(), (return_value, current_time))

        def _get_dictionaries(self, inst = "this.is.not.an.instance"):
            if inst == "this.is.not.an.instance":
                inst = self._inst
            if not inst in self.dictionaries_per_inst:
                self.lock.acquire()
                try:
                    # Double ask, just to avoid acquiring and releasing
                    # without need
                    if not inst in self.dictionaries_per_inst:
                        self.dictionaries_per_inst[inst] = {
                            'dict' : {},
                            'list' : []
                        }
                finally:
                    self.lock.release()
            return self.dictionaries_per_inst[inst]

        def get_time(self):
            return self._time

        def set_time(self, value):
            self._time = value

        time = property(get_time, set_time)

        def _remove_obj(self, key, inst):
            try:
                returnValue, _ = key.pop(self._get_dictionaries(inst))
            except KeyError:
                return

    def wrapped_decorator(func):
        o = cache_obj(func)
        o.__name__ = func.__name__
        o.__doc__  = func.__doc__
        return o

    return wrapped_decorator

class fast_cache(object):
    """ Fastest cache. Problems:
    a) Can't be used with unhashable types (dictionaries, lists, etc.)
    b) Doesn't support key arguments
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
        self._inst = None
        _fast_cache_registry.append(self)

    def __get__(self, inst, owner):
        self._inst = weakref.ref(inst)
        return self

    def __call__(self, *args):
        try:
            if self._inst is not None:
                args = (self._inst(),) + args

            if args in self.cache:
                return self.cache[args]
            else:
                return_value = self.func(*args)
                self.cache[args] = return_value
                return return_value
        except TypeError:
            print("Using fast_cache with func {0}, a function that might receive unhashable arguments!!!".format(self.func), file=sys.stderr)
            return self.func(*args)

