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

import os
import time

from optparse import OptionParser

from weblab.admin.script.utils import check_dir_exists

from weblab.admin.monitor.monitor import WebLabMonitor
import weblab.core.coordinator.status as WebLabQueueStatus


#########################################################################################
# 
# 
# 
#      W E B L A B     M O N I T O R I N G
# 
# 
# 

def weblab_monitor(directory):
    check_dir_exists(directory)
    new_globals = {}
    new_locals  = {}
    execfile(os.path.join(directory, 'debugging.py'), new_globals, new_locals)

    SERVERS = new_locals['SERVERS']

    def list_users(experiment):
        information, ups_orphans, coordinator_orphans = wl.list_users(experiment)

        print("%15s\t%25s\t%11s\t%11s" % ("LOGIN","STATUS","UPS_SESSID","RESERV_ID"))
        for login, status, ups_session_id, reservation_id in information:
            if isinstance(status, WebLabQueueStatus.WaitingQueueStatus) or isinstance(status, WebLabQueueStatus.WaitingInstancesQueueStatus):
                status_str = "%s: %s" % (status.status, status.position)
            else:
                status_str = status.status

            if options.full_info:
                    print("%15s\t%25s\t%8s\t%8s" % (login, status_str, ups_session_id, reservation_id))
            else:
                    print("%15s\t%25s\t%8s...\t%8s..." % (login, status_str, ups_session_id[:8], reservation_id))

        if len(ups_orphans) > 0:
            print()
            print("UPS ORPHANS")
            for ups_info in ups_orphans:
                print(ups_info)

        if len(coordinator_orphans) > 0:
            print()
            print("COORDINATOR ORPHANS")
            for coordinator_info in coordinator_orphans:
                print(coordinator_info)

    def show_server(number):
        if number > 0:
            print()
        print("Server %s" % (number + 1))

    option_parser = OptionParser()

    option_parser.add_option( "-e", "--list-experiments",
                              action="store_true",
                              dest="list_experiments",
                              help="Lists all the available experiments" )
                            
    option_parser.add_option( "-u", "--list-users",
                              dest="list_users",
                              nargs=1,
                              default=None,
                              metavar='EXPERIMENT_ID',
                              help="Lists all users using a certain experiment (format: experiment@category)" )

    option_parser.add_option( "-a", "--list-experiment-users",
                              action="store_true",
                              dest="list_experiment_users",
                              help="Lists all users using any experiment" )

    option_parser.add_option( "-l", "--list-all-users",
                              action="store_true",
                              dest="list_all_users",
                              help="Lists all connected users" )

    option_parser.add_option( "-f", "--full-info",
                      action="store_true",
                              dest="full_info",
                              help="Shows full information (full session ids instead of only the first characteres)" )
                             
    option_parser.add_option( "-k", "--kick-session",
                              dest="kick_session",
                              nargs=1,
                              default=None,
                              metavar='SESSION_ID',
                              help="Given the full UPS Session ID, it kicks out a user from the system" )

    option_parser.add_option( "-b", "--kick-user",
                              dest="kick_user",
                              nargs=1,
                              default=None,
                              metavar='USER_LOGIN',
                              help="Given the user login, it kicks him out from the system" )

    options, _ = option_parser.parse_args()

    for num, server in enumerate(SERVERS):
        wl = WebLabMonitor(server)

        if options.list_experiments:
            print(wl.list_experiments(), end='')

        elif options.list_experiment_users:
            show_server(num)
            experiments = wl.list_experiments()
            if experiments != '':
                for experiment in experiments.split('\n')[:-1]:
                    print()
                    print("%s..." % experiment)
                    print()
                    list_users(experiment)
            
        elif options.list_users != None:
            show_server(num)
            list_users(options.list_users)
            
        elif options.list_all_users:
            show_server(num)
            all_users = wl.list_all_users()

            print("%15s\t%11s\t%17s\t%24s" % ("LOGIN","UPS_SESSID","FULL_NAME","LATEST TIMESTAMP"))

            for ups_session_id, user_information, latest_timestamp in all_users:
                latest = time.asctime(time.localtime(latest_timestamp))
                if options.full_info:
                    print("%15s\t%11s\t%17s\t%24s" % (user_information.login, ups_session_id.id, user_information.full_name, latest))
                else:
                    if len(user_information.full_name) <= 14:
                        print("%15s\t%8s...\t%s\t%24s" % (user_information.login, ups_session_id.id[:8], user_information.full_name, latest))
                    else:
                        print("%15s\t%8s...\t%14s...\t%24s" % (user_information.login, ups_session_id.id[:8], user_information.full_name[:14], latest))
            
        elif options.kick_session != None:
            show_server(num)
            wl.kick_session(options.kick_session)

        elif options.kick_user != None:
            show_server(num)
            wl.kick_user(options.kick_user)
           
        else:
            option_parser.print_help()
            break


