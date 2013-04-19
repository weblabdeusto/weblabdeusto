#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

import os
import sys

import signal

from optparse import OptionParser

from weblab.admin.script.utils import check_dir_exists
from voodoo.gen.loader.ConfigurationParser import GlobalParser

#########################################################################################
# 
# 
# 
#      W E B L A B     R U N N I N G      A N D     S T O P P I N G 
# 
# 
# 

def weblab_start(directory):
    parser = OptionParser(usage="%prog create DIR [options]")

    parser.add_option("-m", "--machine",           dest="machine", default=None, metavar="MACHINE",
                                                   help = "If there is more than one machine in the configuration, which one should be started.")
    parser.add_option("-l", "--list-machines",     dest="list_machines", action='store_true', default=False, 
                                                   help = "List machines.")

    parser.add_option("-s", "--script",            dest="script", default=None, metavar="SCRIPT",
                                                   help = "If the runner option is not available, which script should be used.")

    options, args = parser.parse_args()

    check_dir_exists(directory, parser)

    old_cwd = os.getcwd()
    os.chdir(directory)
    try:
        if options.script: # If a script is provided, ignore the rest
            if os.path.exists(options.script):
                execfile(options.script)
            elif os.path.exists(os.path.join(old_cwd, options.script)):
                execfile(os.path.join(old_cwd, options.script))
            else:
                print >> sys.stderr, "Provided script %s does not exist" % options.script
                sys.exit(-1)
        else:
            parser = GlobalParser()
            global_configuration = parser.parse('.')
            if options.list_machines:
                for machine in global_configuration.machines:
                    print ' - %s' % machine
                sys.exit(0)

            machine_name = options.machine
            if machine_name is None: 
                if len(global_configuration.machines) == 1:
                    machine_name = global_configuration.machines.keys()[0]
                else:
                    print >> sys.stderr, "System has more than one machine (see -l). Please detail which machine you want to start with the -m option."
                    sys.exit(-1)

            if not machine_name in global_configuration.machines:
                print >> sys.stderr, "Error: %s machine does not exist. Use -l to see the list of existing machines." % machine_name
                sys.exit(-1)

            machine_config = global_configuration.machines[machine_name]
            if machine_config.runner is None:
                if os.path.exists('run.py'):
                    execfile('run.py')
                else:
                    print >> sys.stderr, "No runner was specified, and run.py was not available. Please the -s argument to specify the script or add the <runner file='run.py'/> option in %s." % machine_name
                    sys.exit(-1)
            else:
                if os.path.exists(machine_config.runner):
                    execfile(machine_config.runner)
                else:
                    print >> sys.stderr, "Misconfigured system. Machine %s points to %s which does not exist." % (machine_name, os.path.abspath(machine_config.runner))
                    sys.exit(-1)
    finally:
        os.chdir(old_cwd)

def weblab_stop(directory):
    parser = OptionParser(usage="%prog stop DIR [options]")

    check_dir_exists(directory, parser)
    if sys.platform.lower().startswith('win'):
        print >> sys.stderr, "Stopping not yet supported. Try killing the process from the Task Manager or simply press enter"
        sys.exit(-1)
    os.kill(int(open(os.path.join(directory, 'weblab.pid')).read()), signal.SIGTERM)


