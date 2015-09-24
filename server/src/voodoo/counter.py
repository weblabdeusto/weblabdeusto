#!/usr/bin/env python
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

_counters = {}
_counter_lock = threading.Lock()

def next_counter(name):
    with _counter_lock:
        cur = _counters[name] = _counters.get(name, 0) + 1
    return cur

def next_name(name):
    return "%s-%i" % (name, next_counter(name))

