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

import os
import sys
from optparse import OptionParser

COMMANDS = {
    'create'     : 'Create a new weblab instance', 
    'rebuild-db' : 'Rebuild the database of the weblab instance', 
    'start'      : 'Start an existing weblab instance', 
    'stop'       : 'Stop an existing weblab instance',
    'admin'      : 'Adminstrate a weblab instance',
    'monitor'    : 'Monitor the current use of a weblab instance',
}

def weblab():
    if len(sys.argv) in (1, 2) or sys.argv[1] not in COMMANDS:
        command_list = ""
        for command, help_text in COMMANDS.items():
            command_list += "\t%s\t\t%s\n" % (command, help_text)
        print >> sys.stderr, "Usage: %s option DIR [option arguments]\n\n%s\n" % (sys.argv[0], command_list)
        sys.exit(0)
    main_command = sys.argv[1]
    if main_command == 'create':
        weblab_create(sys.argv[2])
    else:
        print >>sys.stderr, "Command %s not yet implemented" % sys.argv[1]

COORDINATION_ENGINES = ['sql',   'redis'  ]
DATABASE_ENGINES     = ['mysql', 'sqlite' ]
SESSION_ENGINES      = ['sql',   'redis', 'memory']

def weblab_create(directory):
    parser = OptionParser(usage="%prog create DIR [options]")

    parser.add_option("--cores",                  dest="cores",           type="int",    default=1,
                                                  help = "Number of core servers.")

    parser.add_option("--start-port",             dest="start_ports",     type="int",    default=10000,
                                                  help = "From which port start counting.")

    parser.add_option("--db-engine",              dest="db_engine",       choices = DATABASE_ENGINES,
                                                  help = "Database engine to use. Values: %s." % (', '.join(DATABASE_ENGINES)))

    parser.add_option("--coordination-engine",    dest="coord_engine",    choices = COORDINATION_ENGINES,
                                                  help = "Coordination engine used. Values: %s." % (', '.join(COORDINATION_ENGINES)))

    parser.add_option("--coordination-db-engine", dest="coord_db_engine", choices = DATABASE_ENGINES,
                                                  help = "Coordination database engine used, if the coordination is based on a database. Values: %s." % (', '.join(DATABASE_ENGINES)))

    parser.add_option("--session-storage",        dest="session_storage", choices = SESSION_ENGINES,
                                                  help = "Session storage used. Values: %s." % (', '.join(SESSION_ENGINES)) )

    parser.add_option("--inline-lab-server",      dest="inline_lab_serv", action="store_true", default=False,
                                                  help = "Laboratory server included in the same process as the core server. " 
                                                         "Only available if a single core is used." )

    parser.add_option("-f", "--force",            dest="force", action="store_true", default=False,
                                                   help = "Overwrite the contents even if the directory already existed.")

    (options, args) = parser.parse_args()

    if os.path.exists(directory) and not options.force:
        print >> sys.stderr, "ERROR: Directory %s already exists. Use --force if you want to overwrite the contents." % directory
        sys.exit(-1)
    
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            print >> sys.stderr, "ERROR: %s is not a directory. Delete it before proceeding." % directory
            sys.exit(-1)
    else:
        try:

            os.mkdir(directory)
        except Exception as e:
            print >> sys.stderr, "ERROR: Could not create directory %s: %s" % (directory, str(e))
            sys.exit(-1)

    print options.cores, options.db_engine, options.inline_lab_serv

