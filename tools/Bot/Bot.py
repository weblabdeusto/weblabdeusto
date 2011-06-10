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
sys.path.append(os.sep.join(('..','..','server','src')))

import datetime
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle

import libraries
import Configuration as Cfg

from weblab.admin.bot.Launcher import BotLauncher

if __name__ == "__main__":

    now = datetime.datetime.now()
    execution_unique_id = 'D_%s_%s_%s_T_%s_%s_%s_' % (
                ('%s' % now.year).zfill(4),
                ('%s' % now.month).zfill(2),
                ('%s' % now.day).zfill(2),
                ('%s' % now.hour).zfill(2),
                ('%s' % now.minute).zfill(2),
                ('%s' % now.second).zfill(2)
            )

    execution_results = {}

    for num_scenario, scenario in enumerate(Cfg.SCENARIOS):

        if not scenario.category in execution_results:
            execution_results[scenario.category] = {}

        for num_configuration, configuration in enumerate(Cfg.CONFIGURATIONS):
            pickle_filename = "logs" + os.sep + "botclient_%s_SCEN_%s_CONFIG_%s.pickle" % (
                                    execution_unique_id, 
                                    str(num_scenario).zfill(len(str(len(Cfg.SCENARIOS)))), 
                                    str(num_configuration).zfill(len(str(len(Cfg.CONFIGURATIONS))))
                            )
            botlauncher = BotLauncher(
                Cfg.WEBLAB_PATH,
                configuration,
                Cfg.HOST,
                pickle_filename,
                "logging.cfg",
                scenario=scenario.users, 
                iterations=Cfg.ITERATIONS,
                ports=Cfg.PORTS[configuration]
            )
                
            botlauncher.start()
            
            print "   -> Scenario: %s" % scenario
            print "   -> Results stored in %s" % pickle_filename
            print "   -> Serializing results..."
            result = botlauncher.get_results()
            execution_results[scenario.category][scenario.identifier] = result
            print "   -> Done"

    raw_information = {}
    for category in execution_results:
        x = [ key for key in execution_results[category].keys() ]
        y = [ execution_results[category][key] for key in x ]
        raw_information[category] = (x,y)

    try:
        results_filename = "raw_information_%s.dump" % execution_unique_id
        print "Writing results to file %s... %s" % (results_filename, datetime.datetime.now())
        results_file = open(results_filename, 'w')
        pickle.dump(raw_information, results_file)
    except:
        print "There was an error writing results to file"
        import traceback
        traceback.print_stack()

    if Cfg.GENERATE_GRAPHICS:
        print "Generating graphics..."
        try:
            import BotGraphics
            BotGraphics.print_results(raw_information, execution_unique_id, True)
        except ImportError:
            print "Couldn't generate graphics. Maybe matplotlib.pyplot is not installed? See http://matplotlib.sourceforge.net/"
    else:
        print "Not generating graphics"

    print "Done", datetime.datetime.now()
    


