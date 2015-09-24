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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

import sys

import time
import cPickle as pickle
import logging.config

import weblab.admin.bot.wl_process as WebLabProcess
import weblab.admin.bot.data as Data

import voodoo.mapper as mapper

class BotLauncher(object):

    def __init__(self, configuration, host, pickle_file_name, logging_cfg_file_name, scenario, iterations, options, verbose):
        super(BotLauncher, self).__init__()
        self.verbose = verbose
        self.options = options
        if isinstance(configuration, basestring):
            self.launch_files = [ configuration ]
        else:
            self.launch_files = configuration
        self.host = host
        self.pickle_file_name = pickle_file_name
        self.logging_cfg_file_name = logging_cfg_file_name
        self.scenario = scenario
        self.iterations = iterations
        self.results = []

        self._set_logging_cfg()
        self._set_users()

    def _set_logging_cfg(self):
        logging.config.fileConfig(self.logging_cfg_file_name)

    def _set_users(self):
        self.users = len(self.scenario)

    def _add_exception(self, exceptions_dict, (exception, trace)):
        """ { "ExceptionType1": <BotError>, "ExceptionType2": <BotError>, ... } """
        if exception.__class__.__name__ in exceptions_dict:
            exceptions_dict[exception.__class__.__name__].add_instance((exception, trace))
        else:
            exceptions_dict[exception.__class__.__name__] = Data.BotError((exception, trace))

    def _print(self, message):
        sys.stdout.write(message)
        sys.stdout.flush()

    def _dump_results(self):
        results     = self.get_results()
        pickle_file = open(self.pickle_file_name,'w')
        pickle.dump(results, pickle_file)

    def _load_results(self):
        pickle.load(open(self.pickle_file_name,'r'))

    def start(self):
        # Launching trials...
        print("New trial. %i iterations" % self.iterations)
        self.bot_trial = self._launch_trial()

        print("Cleaning results...", time.asctime())
        self.bot_trial = mapper.remove_unpickables(self.bot_trial)

        if self.pickle_file_name is not None:
            try:
                print("Storing results...", time.asctime())
                self._dump_results()
                print("Results stored",time.asctime())
            except Exception as e:
                print("Error: Couldn't store results into %s: %r" % (self.pickle_file_name, e))

    def _launch_trial(self):

        # Launching iterations...
        iterations = []
        for i in range(self.iterations):
            self._print(" iteration %i " % i)
            bot_iteration = self._launch_iteration()
            self._print(" [ %s exceptions ] " % len(bot_iteration.exceptions))
            iterations.append(bot_iteration)
            self._print("\n")

        return Data.BotTrial(iterations)

    def _start_processes(self):
        if self.options['dont_start_processes']:
            time.sleep(10)
            return
        started_processes = []
        try:
            for launch_file in self.launch_files:
                if self.verbose:
                    print("[Launcher] Launching... %s" % launch_file)
                weblab_process = WebLabProcess.WebLabProcess(launch_file, self.host, self.options, verbose = self.verbose)
                weblab_process.start()
                if self.verbose:
                    print("[Launcher] %s running" % launch_file)
                started_processes.append(weblab_process)

            if len(started_processes) > 1:
                started_processes[0].step_wait()

            for weblab_process in started_processes:
                weblab_process.wait_for_process_started()

            if len(started_processes) > 1:
                started_processes[0].step_started_wait()
        except:
            for started_process in started_processes:
                if self.verbose:
                    print("[Launcher] Shutting down... %s" % started_process)
                started_process.shutdown()
            raise
        return started_processes

    def _stop_processes(self, started_processes):
        if self.options['dont_start_processes']:
            return 'Nothing started', 'Nothing started'

        complete_out = ''
        complete_err = ''
        for started_process in started_processes:
            started_process.shutdown()
            complete_out += started_process.out
            complete_err += started_process.err
        return complete_out, complete_err

    def _launch_iteration(self):
        started_processes = self._start_processes()

        # Launching botusers...
        if self.verbose:
            print("[Launcher] All processes launched")
        try:
            botusers = []
            for botuser_creator_name, botuser_creator in self.scenario:
                botusers.append(botuser_creator())

            begin_time = time.time()
            for botuser in botusers:
                botuser.start()

            waiting_botusers = botusers[:]
            while len(waiting_botusers) > 0:
                number_before = len(waiting_botusers)
                waiting_botusers = [ botuser for botuser in waiting_botusers if botuser.isAlive() ]
                for _ in range(number_before - len(waiting_botusers)):
                        self._print(".")
                time.sleep(0.3)
            iteration_time = time.time() - begin_time
        finally:
            complete_out, complete_err = self._stop_processes(started_processes)

        botuser_routes = [ botuser.route for botuser in botusers ]
        routes = {}
        for route in botuser_routes:
            if route in routes:
                routes[route] = routes[route] + 1
            else:
                routes[route] = 1

        self._print("  %s" % routes)

        # Compiling iteration data...
        exceptions = {}
        for botuser in botusers:
            for exception, trace in botuser.get_exceptions():
                self._add_exception(exceptions, (exception, trace))
        return Data.BotIteration(iteration_time, exceptions, botusers, complete_out, complete_err)

    def len(self):
        return self.users / self.step

    def get_results(self):
        return self.bot_trial

