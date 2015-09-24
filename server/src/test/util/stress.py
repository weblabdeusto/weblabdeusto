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


import time
import time as time_module
import threading
import voodoo.counter as counter

DEBUGGING = True

def avg(l):
    total = 0
    for value in l:
        total += value
    return float(total) / len(l)

class RunningThread(threading.Thread):
    def __init__(self, condition, iterations, func, name):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("RunningThread_%s" % self.name))
        self.condition     = condition
        self.func          = func
        self.times         = []
        self.iterations    = iterations
        self.waiting       = False

    def run(self):
        self.condition.acquire()
        try:
            self.waiting = True
            self.condition.wait()
        finally:
            self.condition.release()

        for _ in xrange(self.iterations):
            t1 = time.time()
            self.func()
            t2 = time.time()
            self.times.append(t2 - t1)

class ThreadedRunner(object):
    MAX_WAITING_TIME = 15

    def __init__(self, func, threads, iterations, name):
        self.func       = func
        self.threads    = threads
        self.iterations = iterations
        self.name       = name
        self.times      = []

    def run(self):
        condition = threading.Condition()
        threads = []
        for _ in xrange(self.threads):
            thread = RunningThread(condition, self.iterations, self.func, self.name)
            threads.append(thread)

        for thread in threads:
            thread.start()

        while len([ t for t in threads if t.waiting ]) != self.threads:
            time_module.sleep(0.05)

        condition.acquire()
        try:
            condition.notifyAll()
        finally:
            condition.release()

        self.times = []
        if DEBUGGING:
            import sys, time
            start_time = time.time()
            waiting_threads = threads[:]
            while len(waiting_threads) > 0:
                number_before = len(waiting_threads)
                waiting_threads = [ t for t in waiting_threads if t.isAlive() ]
                for _ in xrange(number_before - len(waiting_threads)):
                    sys.stdout.write('.')
                    sys.stdout.flush()
                time.sleep(0.1)
                if time.time() - start_time > self.MAX_WAITING_TIME:
                    break
            print
        for thread in threads:
            thread.join(self.MAX_WAITING_TIME)
            if not thread.isAlive():
                self.times.extend(thread.times)
        return self.times

class SequentialRunner(object):
    def __init__(self, func, iterations, name):
        self.func       = func
        self.iterations = iterations
        self.name       = name
        self.times      = []

    def run(self):
        self.times = []
        for _ in xrange(self.iterations):
            t1 = time.time()
            self.func()
            t2 = time.time()
            self.times.append(t2 - t1)
        return self.times

class MainRunner(object):

    MATPLOTLIB_BACKEND      = 'Agg'
    DEFAULT_NUMBER_OF_TIMES =  2

    matplotlib = None
    plt        = None

    def __init__(self, func, name, assert_klass = AssertionError):
        self.func = func
        self.name = name
        self.assert_klass = assert_klass

        self.runner = None

    def run_threaded(self, threads, iterations, max_time):
        self.runner = ThreadedRunner(self.func, threads, iterations, self.name)
        return self._run(self.runner, max_time)

    def run_sequential(self, iterations, max_time):
        self.runner = SequentialRunner(self.func, iterations, self.name)
        return self._run(self.runner, max_time)

    def _run(self, runner, max_time):
        times = runner.run()
        slow_times = [ t for t in times if t > max_time]
        if len(slow_times) > 0:
            raise self.assert_klass("MainRunner %s; Too slow: %s; avg = %s; max = %s which > %s" % (self.name, slow_times, avg(times), max(slow_times), max_time))
        return times

    def print_graphics_threaded(self, filename, threads_configurations, iterations, number_of_times = None):
        if number_of_times is None:
            number_of_times = self.DEFAULT_NUMBER_OF_TIMES

        total_results = []
        last_times = []
        for _ in xrange(number_of_times):
            results = []

            for threads in threads_configurations:
                if DEBUGGING:
                    print("    running %s threads..." % threads)
                runner = ThreadedRunner(self.func, threads, iterations, self.name)
                times = runner.run()
                max_time = max(times)
                avg_time = avg(times)
                min_time = min(times)
                results.append((threads, max_time, avg_time, min_time))

            last_times.append(times)
            total_results.append(results)

        self._print_results('threads', total_results, filename, last_times)

    def print_graphics_sequential(self, filename, iterations_configurations, number_of_times = None):
        if number_of_times is None:
            number_of_times = self.DEFAULT_NUMBER_OF_TIMES

        total_results = []
        last_times    = []

        for _ in xrange(number_of_times):
            results = []

            for iterations in iterations_configurations:
                if DEBUGGING:
                    print("    running %s iterations..." % iterations)
                runner = SequentialRunner(self.func, iterations, self.name)
                times = runner.run()
                max_time = max(times)
                avg_time = avg(times)
                min_time = min(times)
                results.append((iterations, max_time, avg_time, min_time))

            last_times.append(times)
            total_results.append(results)

        self._print_results('iterations', total_results, filename, last_times)

    def _print_results(self, variable, total_results, filename, last_times):

        grouped_results = [ zip(*new_results) for new_results in zip(*total_results) ]
        results = [ (variables[0], avg(max_n), avg(avg_n), avg(min_n)) for variables, max_n, avg_n, min_n in grouped_results ]

        if self.matplotlib is None:
            import matplotlib
            matplotlib.use(self.MATPLOTLIB_BACKEND)
            import matplotlib.pyplot as plt

            MainRunner.matplotlib = matplotlib
            MainRunner.plt        = plt

        xs     = []
        ys_max = []
        ys_avg = []
        ys_min = []
        for variable, max_time, avg_time, min_time in results:
            xs.append(variable)
            ys_max.append(max_time)
            ys_avg.append(avg_time)
            ys_min.append(min_time)

        fig = self.plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(xs, ys_max, 'r-')
        ax.plot(xs, ys_avg, 'g-')
        ax.plot(xs, ys_min, 'b-')

        xlabel = 'red: max; green: avg; blue: min\nfunc: %s; variable: %s' % (self.func.__name__, variable)
        ax.set_xlabel(xlabel)
        self.plt.savefig(filename)

        fig = self.plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(xs, ys_avg, 'g-')
        ax.plot(xs, ys_min, 'b-')

        xlabel = 'green: avg; blue: min\nfunc: %s; variable: %s' % (self.func.__name__, variable)
        ax.set_xlabel(xlabel)
        self.plt.savefig(filename.replace('.png','_without_max.png'))

        # Now the distribution of the last sample

        for times in last_times:
            times.sort()

        avg_times = [ avg(x) for x in zip(*last_times) ]
        max_time  = max(avg_times)
        intervals = 200
        interval_size = 1.0 * max_time / intervals

        xs = []
        ys = []

        for interval_number in xrange(intervals):
            max_size = (interval_number + 1) * interval_size
            min_size = interval_number * interval_size
            avg_size = (max_size + min_size) / 2.0
            xs.append(avg_size)
            ys.append(len([ t for t in avg_times if t > min_size and t <= max_size]))


        fig = self.plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(xs, ys, 'b-')
        xlabel = 'Distribution'
        ax.set_xlabel(xlabel)
        self.plt.savefig(filename.replace('.png','_last_distribution.png'))

        fig = self.plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(xs, ys, 'b-')
        xlabel = 'Distribution'
        ax.set_xlabel(xlabel)
        ax.axis([0,max_time,0,15])
        self.plt.savefig(filename.replace('.png','_last_distribution_tail.png'))


