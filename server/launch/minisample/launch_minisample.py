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

import sys
sys.path.append('../../src')

def inner(signals = False, condition = None, event_notifier = None):
    def before_shutdown():
        print "Stopping servers..."

    import signal
    import voodoo.gen.launcher as Launcher
    import voodoo.rt_debugger as rt_debugger

    rt_debugger.launch_debugger()

    if condition is not None:
        waiters = ( Launcher.ConditionWait(condition), )
    elif signals:
        waiters = (
                Launcher.SignalWait(signal.SIGTERM),
                Launcher.SignalWait(signal.SIGINT),
                Launcher.RawInputWait("Press <enter> or send a sigterm or a sigint to finish.\n"),
            )
    else:
        waiters = (
                Launcher.RawInputWait("Control+C to finish.\n"),
            )

    event_notifiers = (
                 Launcher.FileNotifier("_file_notifier", "server started"),
            )
    if event_notifier:
        event_notifiers += ( Launcher.ConditionNotifier(event_notifier),)

    launcher = Launcher.Launcher(
            '.',
            'myhost',
            'myprocess',
            waiters,
            "logging.configuration.txt",
            before_shutdown,
            event_notifiers
        )
    launcher._wait_condition = condition
    return launcher

def launch(signals = False):
    launcher = inner(signals = signals)
    launcher.launch()
    return launcher

if __name__ == '__main__':
    try:
        from werkzeug.serving import run_with_reloader
    except ImportError:
        print "werkzeug.serving not installed (pip install werkzeug). If you're developing, you'll have to restart the application in every change manually."
        launch(signals = True)
    else:
        run_with_reloader(launch)
    
