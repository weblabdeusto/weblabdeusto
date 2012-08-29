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
import os

import datetime
import time
import cPickle as pickle

from optparse import OptionParser

from weblab.admin.bot.graphics import print_results
from weblab.admin.bot.launcher import BotLauncher

def main():
    parser = OptionParser(usage="%prog [options]")

    parser.add_option("-c", "--configuration-file", dest="configuration_file", default='configuration.py',
                                                    help = "Configuration file to use.")

    parser.add_option("-v", "--verbose",            dest="verbose", default=False, action='store_true',
                                                    help = "Show more information")

    options, args = parser.parse_args()

    if not os.path.exists(options.configuration_file):
        print >> sys.stderr, "Configuration file %s does not exist. Provide an existing one with the -c option " % options.configuration_file
        sys.exit(-1)

    class Configuration(object):
        execfile(options.configuration_file)

        def get(self, name, default = None):
            return getattr(self, name, default)

        def __getitem__(self, name):
            if not hasattr(self, name):
                raise AttributeError('Holder does not have %s' % name)
            return getattr(self, name)

    variables = {}
    execfile(options.configuration_file, variables, variables)

    cfg = Configuration()
    verbose = cfg.get('VERBOSE', False) or options.verbose 

    if not os.path.exists('logs'): 
        os.mkdir('logs')

    if not os.path.exists('figures'):
        os.mkdir('figures')

    for num_configuration, configuration in enumerate(cfg.CONFIGURATIONS):
        now = datetime.datetime.now()
        execution_unique_id = 'D_%s_%s_%s_T_%s_%s_%s_' % (
                    ('%s' % now.year).zfill(4),
                    ('%s' % now.month).zfill(2),
                    ('%s' % now.day).zfill(2),
                    ('%s' % now.hour).zfill(2),
                    ('%s' % now.minute).zfill(2),
                    ('%s' % now.second).zfill(2)
                )
        print 
        print "*" * 20
        print "CONFIGURATION %s" % str(configuration)
        print "Unique id: %s" % execution_unique_id
        print "*" * 20
        print 

        execution_results = {}

        scenarios = variables['generate_scenarios']()
        for num_scenario, scenario in enumerate(scenarios):

            if not scenario.category in execution_results:
                execution_results[scenario.category] = {}

            pickle_filename = "logs" + os.sep + "botclient_%s_SCEN_%s_CONFIG_%s.pickle" % (
                                    execution_unique_id, 
                                    str(num_scenario).zfill(len(str(len(scenarios)))), 
                                    str(num_configuration).zfill(len(str(len(cfg.CONFIGURATIONS))))
                            )
            botlauncher = BotLauncher(
                configuration,
                cfg.HOST,
                pickle_filename,
                "logging.cfg",
                scenario=scenario.users, 
                iterations=cfg.ITERATIONS,
                verbose = verbose,
            )
                
            botlauncher.start()
            
            print "   -> Scenario: %s" % scenario
            print "   -> Results stored in %s" % pickle_filename
            print "   -> Serializing results..."
            result = botlauncher.get_results()
            del botlauncher
            execution_results[scenario.category][scenario.identifier] = result
            print "   -> Done"
            scenario.dispose()

        raw_information = {}
        for category in execution_results:
            x = [ key for key in execution_results[category].keys() ]
            y = [ execution_results[category][key] for key in x ]
            raw_information[category] = (x,y)

        del execution_results

        try:
            results_filename = "raw_information_%s.dump" % execution_unique_id
            print "Writing results to file %s... %s" % (results_filename, datetime.datetime.now())
            results_file = open(results_filename, 'w')
            pickle.dump(raw_information, results_file)
        except:
            print "There was an error writing results to file"
            import traceback
            traceback.print_stack()

        if cfg.GENERATE_GRAPHICS:
            print "Generating graphics..."
            print_results(raw_information, configuration, execution_unique_id, cfg, True)
        else:
            print "Not generating graphics"

        print "Done", datetime.datetime.now()
        del raw_information

