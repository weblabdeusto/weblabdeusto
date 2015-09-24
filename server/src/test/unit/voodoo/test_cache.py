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

import unittest
#import time

import voodoo.cache as cache

sample_decorator_func = None

def sample_decorator(func):
    def wrapped_decorator(*args, **kargs):
        return func(*args, **kargs)

    global sample_decorator_func
    sample_decorator_func = func
    wrapped_decorator.__doc__ = func.__doc__
    wrapped_decorator.__name__ = func.__name__
    return wrapped_decorator

class CacheTestCase(unittest.TestCase):
    def test_cache_unpickable_objs(self):
        wait_time  = 0.4
        self._call_times = 0

        @cache.cache(wait_time)
        def whatever(arg):
            self._call_times += 1
            return arg

        read_file = open(__file__)

        result = whatever(arg=read_file)
        self.assertEquals(
                read_file,
                result
            )
        self.assertEquals(
                1,
                self._call_times
            )

        result = whatever(arg=read_file)
        self.assertEquals(
                read_file,
                result
            )
        self.assertEquals(
                1,
                self._call_times
            )

        other_read_file = open(__file__)
        result = whatever(arg=other_read_file)
        self.assertEquals(
                other_read_file,
                result
            )
        self.assertEquals(
                2,
                self._call_times
            )

    def test_cache_pickable_objs(self):
        wait_time  = 0.4
        self._call_times = 0

        @cache.cache(wait_time)
        def whatever(arg):
            self._call_times += 1
            return arg

        foo = {}
        result = whatever(foo)
        self.assertEquals(
                foo,
                result
            )
        self.assertEquals(
                1,
                self._call_times
            )

        result = whatever(foo)
        self.assertEquals(
                foo,
                result
            )
        self.assertEquals(
                1,
                self._call_times
            )

        bar = {"foo":"bar"}
        result = whatever(bar)
        self.assertEquals(
                bar,
                result
            )
        self.assertEquals(
                2,
                self._call_times
            )

    def test_no_timeout(self):
        self._call_times = 0
        @cache.cache()
        def forever(arg):
            self._call_times += 1
            return arg

        self.assertEquals(5, forever(5))
        self.assertEquals(1, self._call_times)

        self.assertEquals(5, forever(5))
        # Still 1
        self.assertEquals(1, self._call_times)

    def test_cache_generator(self):
        wait_time  = 0.4

        @cache.cache(wait_time)
        def fibonacci(n):
            self._calls += 1
            if n in (0,1):
                return n
            return fibonacci(n-1) + fibonacci(n-2)

        self._real_test_fib(fibonacci, wait_time)

    def test_cache_generator_with_object(self):
        wait_time  = 0.4

        class FibonacciClass(object):
            def __init__(self, test_case):
                super(FibonacciClass, self).__init__()
                self._test_case = test_case
            @cache.cache(wait_time)
            def fibonacci(self,n):
                self._test_case._calls += 1
                if n in (0,1):
                    return n
                return self.fibonacci(n-1) + self.fibonacci(n-2)

        fibonacci_instance = FibonacciClass(self)
        self._real_test_fib(fibonacci_instance.fibonacci,wait_time)

    def test_cache_generator_with_multiple_instances(self):
        wait_time  = 1

        class FibonacciClass(object):
            def __init__(self, test_case):
                super(FibonacciClass, self).__init__()
                self._test_case = test_case
            @cache.cache(wait_time)
            def fibonacci(self,n):
                self._test_case._calls += 1
                if n in (0,1):
                    return n
                return self.fibonacci(n-1) + self.fibonacci(n-2)

        cur_time = 10
        def _get_time():
            return cur_time

        FibonacciClass.fibonacci._get_time = _get_time

        fibonacci_instance_A = FibonacciClass(self)
        fibonacci_instance_B = FibonacciClass(self)
        self._calls = 0
        fibonacci_instance_A.fibonacci(1)
        fibonacci_instance_B.fibonacci(1)
        self.assertEquals(2,self._calls)
        fibonacci_instance_A.fibonacci(1)
        fibonacci_instance_A.fibonacci(1)
        fibonacci_instance_B.fibonacci(1)
        fibonacci_instance_B.fibonacci(1)
        self.assertEquals(2,self._calls)

        cur_time += wait_time + 1 # Expired

        fibonacci_instance_A.fibonacci(1)
        fibonacci_instance_B.fibonacci(1)
        self.assertEquals(4,self._calls)
        fibonacci_instance_A.fibonacci(1)
        fibonacci_instance_A.fibonacci(1)
        fibonacci_instance_B.fibonacci(1)
        fibonacci_instance_B.fibonacci(1)
        self.assertEquals(4,self._calls)

    def test_cache_generator_with_old_class(self):
        wait_time  = 0.4

        class FibonacciClass:
            def __init__(self, test_case):
                self._test_case = test_case
            @cache.cache(wait_time)
            def fibonacci(self,n):
                self._test_case._calls += 1
                if n in (0,1):
                    return n
                return self.fibonacci(n-1) + self.fibonacci(n-2)

        fibonacci_instance = FibonacciClass(self)
        self._real_test_fib(fibonacci_instance.fibonacci,wait_time)

    def test_next_decorator(self):
        wait_time  = 0.4

        @cache.cache(wait_time)
        @sample_decorator
        def fibonacci(n):
            self._calls += 1
            if n in (0,1):
                return n
            return fibonacci(n-1) + fibonacci(n-2)

        self._real_test_fib(fibonacci, wait_time)


    def test_previous_decorator(self):
        wait_time  = 0.4

        @sample_decorator
        @cache.cache(wait_time)
        def fibonacci(n):
            self._calls += 1
            if n in (0,1):
                return n
            return fibonacci(n-1) + fibonacci(n-2)

        self._real_test_fib(fibonacci, wait_time)

    def _real_test_fib(self, fibonacci, wait_time):
        self._calls = 0

        # Hook the _create_timer function, so we don't use real timers
        # But FakeTimers
        current_time = 10

        def _get_time():
            return current_time

        global sample_decorator_func
        if sample_decorator_func != None:
            sample_decorator_func._get_time = _get_time
        fibonacci._get_time = _get_time

        # Number of self._calls is always gonna be n + 1
        self.assertEquals(0,fibonacci(0))
        self.assertEquals(0 + 1,self._calls)

        self.assertEquals(1,fibonacci(1))
        self.assertEquals(1 + 1,self._calls)

        # Same number (cached)
        self.assertEquals(1,fibonacci(1))
        self.assertEquals(1 + 1,self._calls)

        # 8 + 1 (no repeated call)
        self.assertEquals(21,fibonacci(8))
        self.assertEquals(8 + 1, self._calls)

        # Same number
        self.assertEquals(13,fibonacci(7))
        self.assertEquals(8 + 1, self._calls)

        current_time += wait_time + 1
        #time.sleep(wait_time * 2)

        before_calls = 8 + 1

        self.assertEquals(13,fibonacci(7))
        self.assertEquals(7 + 1 + before_calls, self._calls)

        self.assertEquals(21,fibonacci(8))
        self.assertEquals(8 + 1 + before_calls, self._calls)

        current_time += wait_time + 1
        #time.sleep(wait_time * 2)

        fibonacci.time = wait_time * 3

        before_calls = 8 + 1 + before_calls

        self.assertEquals(21, fibonacci(8))
        self.assertEquals(8 + 1 + before_calls, self._calls)

        # Now it's not enough time
        #time.sleep(wait_time * 2)

        self.assertEquals(21, fibonacci(8))
        self.assertEquals(8 + 1 + before_calls, self._calls)

class FastCacheTestCase(unittest.TestCase):
    def testFoo(self):

        self._calls = 0

        test_self = self

        class A(object):
            @cache.fast_cache
            def method(self, arg1):
                test_self._calls += 1

        a = A()
        a.method(5)
        self.assertEquals(1, self._calls)
        a.method(5)
        self.assertEquals(1, self._calls)
        b = A()
        b.method(5)
        self.assertEquals(2, self._calls)


def suite():
    return unittest.TestSuite((
                    unittest.makeSuite(CacheTestCase),
                    unittest.makeSuite(FastCacheTestCase)
                ))

if __name__ == '__main__':
    unittest.main()

