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
from __future__ import print_function, unicode_literals

from __future__ import unicode_literals

import os
import sys

import signal

from optparse import OptionParser

from weblab.admin.script.upgrade import check_updated
from weblab.admin.script.utils import check_dir_exists, run_with_config
from voodoo.gen import load_dir

#########################################################################################
# 
# 
# 
#      W E B L A B     R U N N I N G      A N D     S T O P P I N G 
# 
# 
#

def check_pid(pid):
    """
    Check if a process with the specified PID is currently running.
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def weblab_start(directory):
    parser = OptionParser(usage="%prog start DIR [options]")

    parser.add_option('-m', '--host', '--machine',
                                                   dest='host', default=None, metavar='HOST',
                                                   help = 'If there is more than one host in the configuration, which one should be started.')

    parser.add_option('-l', '--list-hosts', '--list-machines',     
                                                   dest='list_hosts', action='store_true', default=False, 
                                                   help = 'List hosts.')

    parser.add_option('-s', '--script',            dest='script', default=None, metavar='SCRIPT',
                                                   help = 'If the runner option is not available, which script should be used.')

    options, args = parser.parse_args()

    check_dir_exists(directory, parser)

    if not run_with_config(directory, check_updated):
        print("Error: WebLab-Deusto instance outdated! You may have updated WebLab-Deusto recently. Run: weblab-admin.py upgrade %s" % directory, file=sys.stderr)
        sys.exit(-1)


    old_cwd = os.getcwd()
    os.chdir(directory)

    # Ensure we aren't already running. The check is not currently supported on Windows.
    if sys.platform.lower().startswith('win'):
        if os.path.exists("weblab.pid"):
            pid = int(open("weblab.pid").read())
            running = check_pid(pid)
            if not running:
                os.remove("weblab.pid")
            else:
                print("Error: WebLab-Deusto instance seems to be running already!", file=sys.stderr)
                sys.exit(-1)

    try:
        if options.script: # If a script is provided, ignore the rest
            if os.path.exists(options.script):
                execfile(options.script)
            elif os.path.exists(os.path.join(old_cwd, options.script)):
                execfile(os.path.join(old_cwd, options.script))
            else:
                print("Provided script %s does not exist" % options.script, file=sys.stderr)
                sys.exit(-1)
        else:
            global_configuration = load_dir('.')
            if options.list_hosts:
                for host in global_configuration:
                    print(' - %s' % host)
                sys.exit(0)

            host_name = options.host
            if host_name is None: 
                if len(global_configuration) == 1:
                    host_name = global_configuration.keys()[0]
                else:
                    print("System has more than one host (see -l). Please detail which host you want to start with the --host option.", file=sys.stderr)
                    sys.exit(-1)

            if not host_name in global_configuration:
                print("Error: %s host does not exist. Use -l to see the list of existing hosts." % host_name, file=sys.stderr)
                sys.exit(-1)

            host_config = global_configuration[host_name]
            if host_config.runner is None:
                if os.path.exists('run.py'):
                    execfile('run.py')
                else:
                    print("No runner was specified, and run.py was not available. Please the -s argument to specify the script or add the <runner file='run.py'/> option in %s." % host_name, file=sys.stderr)
                    sys.exit(-1)
            else:
                if os.path.exists(host_config.runner):
                    execfile(host_config.runner)
                else:
                    print("Misconfigured system. Machine %s points to %s which does not exist." % (host_name, os.path.abspath(host_config.runner)), file=sys.stderr)
                    sys.exit(-1)
    finally:
        os.chdir(old_cwd)

def weblab_stop(directory):
    parser = OptionParser(usage="%prog stop DIR [options]")

    check_dir_exists(directory, parser)
    if sys.platform.lower().startswith('win'):
        print("Stopping not yet supported. Try killing the process from the Task Manager or simply press enter", file=sys.stderr)
        sys.exit(-1)
    os.kill(int(open(os.path.join(directory, 'weblab.pid')).read()), signal.SIGTERM)


