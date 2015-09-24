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

import unittest

import test.util.stress as stress_util

from voodoo.cache import cache, fast_cache

def avg(l):
    total = 0
    for element in l:
        total +=  element
    return 1.0 * total / len(l)

def next_max(l, n):
    new_list = l[:]
    new_list.sort()
    new_list.reverse()
    return new_list[:n]

class CacheTestCase(unittest.TestCase):
    def setUp(self):

        @cache()
        def my_cache_func(arg):
            return arg

        @fast_cache
        def my_fast_cache_func(arg):
            return arg

        def func_cache_hasheable():
            my_cache_func(5)

        self.runner_hasheable = stress_util.MainRunner(func_cache_hasheable, "cache_hasheable")

        def func_cache_pickable():
            my_cache_func({"foo":"bar"})

        self.runner_pickable  = stress_util.MainRunner(func_cache_pickable, "cache_pickable")

        fobj = open(__file__)

        def func_cache_unpickable():
            my_cache_func(arg=fobj)

        self.runner_unpickable  = stress_util.MainRunner(func_cache_unpickable, "cache_unpickable")

        def func_fast_cache():
            my_fast_cache_func(5)

        self.runner_fast  = stress_util.MainRunner(func_fast_cache, "cache_fast")

    def _show_results(self, l):
        return "max: %s; avg: %s; next max: %s" % (max(l), avg(l), next_max(l,4))

    def test_sequential_hasheable(self):
        iterations = 10000
        max_time   = 0.3
        print "seq_hasheable",self._show_results(self.runner_hasheable.run_sequential(iterations, max_time))

    def test_concurrent_hasheable(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con_hasheable",self._show_results(self.runner_hasheable.run_threaded(threads, iterations, max_time))

    def test_sequential_pickable(self):
        iterations = 10000
        max_time   = 0.3
        print "seq_pickable",self._show_results(self.runner_pickable.run_sequential(iterations, max_time))

    def test_concurrent_pickable(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con_pickable",self._show_results(self.runner_pickable.run_threaded(threads, iterations, max_time))

    def test_sequential_unpickable(self):
        iterations = 10000
        max_time   = 0.3
        print "seq_unpickable",self._show_results(self.runner_unpickable.run_sequential(iterations, max_time))

    def test_concurrent_unpickable(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con_unpickable",self._show_results(self.runner_unpickable.run_threaded(threads, iterations, max_time))

    def test_sequential_fast(self):
        iterations = 10000
        max_time   = 0.3
        print "seq_fast",self._show_results(self.runner_fast.run_sequential(iterations, max_time))

    def test_concurrent_fast(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con_fast",self._show_results(self.runner_fast.run_threaded(threads, iterations, max_time))

def suite():
    return unittest.makeSuite(CacheTestCase)

if __name__ == '__main__':
    unittest.main()

