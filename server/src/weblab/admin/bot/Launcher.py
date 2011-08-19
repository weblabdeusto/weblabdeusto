#!/usr/bin/python
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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#

import sys

import time
import cPickle as pickle
import logging.config

import weblab.admin.bot.WebLabProcess as WebLabProcess
import weblab.admin.bot.Data as Data

import voodoo.mapper as mapper

def avg(elements):
    if len(elements) > 0:
        return 1.0 * sum(elements)/len(elements)
    else:
        return 0

class BotLauncher(object):
    
    def __init__(self, weblab_path, launch_file_name, host, pickle_file_name, logging_cfg_file_name, scenario, iterations, ports):
        super(BotLauncher, self).__init__()
        self.weblab_path = weblab_path
        self.launch_file = launch_file_name
        self.host = host
        self.pickle_file_name = pickle_file_name
        self.logging_cfg_file_name = logging_cfg_file_name
        self.scenario = scenario
        self.iterations = iterations
        self.results = []
        self.ports   = ports # { 'soap' : (10123, 20123), ... }

        self._set_logging_cfg()
        self._set_users()
        
    def _set_logging_cfg(self):
        logging.config.fileConfig(self.logging_cfg_file_name)
        
    def _set_users(self):
        self.users = len(self.scenario)
            
    def _add_exception(self, exceptions_dict, (exception, trace)):
        """ { "ExceptionType1": <BotException>, "ExceptionType2": <BotException>, ... } """
        if exceptions_dict.has_key(exception.__class__.__name__):
            exceptions_dict[exception.__class__.__name__].add_instance((exception, trace))
        else:
            exceptions_dict[exception.__class__.__name__] = Data.BotException((exception, trace))

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
        print "New trial. %i iterations" % self.iterations
        self.bot_trial = self._launch_trial()
        
        print "Cleaning results...", time.asctime()
        self.bot_trial = mapper.remove_unpickables(self.bot_trial)

        if self.pickle_file_name is not None:
            try:
                print "Storing results...", time.asctime()
                self._dump_results()
                print "Results stored",time.asctime()
            except Exception as e:
                print "Error: Couldn't store results into %s: %r" % (self.pickle_file_name, e)
        
    def _launch_trial(self):

        # Launching iterations...
        iterations = []
        for i in range(self.iterations):
            self._print(" iteration %i " % i)
            bot_iteration = self._launch_iteration()
            iterations.append(bot_iteration)
            self._print("\n")

        return Data.BotTrial(iterations)

    def _launch_iteration(self):
        
        # Launching botusers...
        self.weblab_process = WebLabProcess.WebLabProcess(self.weblab_path, self.launch_file, self.host, self.ports)
        self.weblab_process.start()
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
            self.weblab_process.shutdown()

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
        return Data.BotIteration(iteration_time, exceptions, botusers, self.weblab_process.out, self.weblab_process.err)
        
    def len(self):
        return self.users / self.step

    def get_results(self):
        return self.bot_trial

