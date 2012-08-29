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
import voodoo.gen.loader.Launcher as Launcher

def before_shutdown():
    print "Stopping servers..."

import voodoo.rt_debugger as rt_debugger
rt_debugger.launch_debugger()

launcher = Launcher.MachineLauncher(
            '.',
            'main_machine',
            (
                Launcher.SignalWait(signal.SIGTERM),
                Launcher.SignalWait(signal.SIGINT),
                Launcher.RawInputWait("Press <enter> or send a sigterm or a sigint to finish\n")
            ),
            "logging.configuration.txt",
            before_shutdown,
            (
                 Launcher.FileNotifier("_file_notifier", "server started"),
            ),
            pid_file = '._machine.pid'
        )
launcher.launch()

