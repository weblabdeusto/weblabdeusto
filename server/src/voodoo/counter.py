#!/usr/bin/env python
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

_counters = {}
_counter_lock = threading.Lock()

def next_counter(name):
    global _counter_lock
    global _counters

    _counter_lock.acquire()
    try:
        if name in _counters:
            _counters[name] = _counters[name] + 1
            cur = _counters[name]
        else:
            _counters[name] = 1
            cur = 1
    finally:
        _counter_lock.release()
    return cur

def next_name(name):
    return "%s-%i" % (name, next_counter(name))

