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

import signal

import sys
sys.path.append('../../src')
import weblab
import voodoo.gen.launcher as Launcher

def before_shutdown():
    print "Stopping servers..."

launcher = Launcher.MachineLauncher(
            '.',
            'main_machine',
            (
                Launcher.SignalWait(signal.SIGTERM),
                Launcher.SignalWait(signal.SIGINT),
                Launcher.RawInputWait("Press <enter> or send a sigterm or a sigint to finish\n")
            ),
            {
                "main_instance1"     : "logging.configuration.server1.txt",
                "main_instance2"     : "logging.configuration.server2.txt",
                "main_instance3"     : "logging.configuration.server3.txt",
                "lab_and_experiment1" : "logging.configuration.other_server1.txt",
                "lab_and_experiment2" : "logging.configuration.other_server2.txt",
            },
            before_shutdown,
            (
                 Launcher.FileNotifier("_file_notifier", "server started"),
            ),
            pid_file = 'sample_balanced1_machine.pid',
            debugger_ports = { 'main_instance1' : 31337, 'main_instance2' : 31338, 'main_instance3' : 31339 }
        )
launcher.launch()

