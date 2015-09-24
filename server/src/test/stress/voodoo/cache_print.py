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

class CachePrintTestCase(unittest.TestCase):
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

    def test_print_results(self):
        threads = []
        for i in xrange(1,5):
            threads.append(i)
        for i in xrange(5,101,5):
            threads.append(i)

        iterations = []
        for i in xrange(1,10001,500):
            iterations.append(i)

        for name in ('hasheable','pickable','unpickable','fast'):
            print "Generating... %s" % name
            print "  threaded..."
            getattr(self,'runner_' + name).print_graphics_threaded  ('logs/results_cache_%s_threaded.png' % name, threads, 50)
            print "  sequential..."
            getattr(self,'runner_' + name).print_graphics_sequential('logs/results_cache_%s_sequential.png' % name, iterations)


def suite():
    return unittest.makeSuite(CachePrintTestCase)

if __name__ == '__main__':
    unittest.main()

