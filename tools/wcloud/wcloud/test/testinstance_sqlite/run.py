#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
try:
    import signal
    
    import voodoo.gen.loader.Launcher as Launcher
    
    def before_shutdown():
        print "Stopping servers..."
    
    launcher = Launcher.MachineLauncher(
                '.',
                'core_machine',
                (
                    Launcher.SignalWait(signal.SIGTERM),
                    Launcher.SignalWait(signal.SIGINT),
                    Launcher.RawInputWait("Press <enter> or send a sigterm or a sigint to finish\n")
                ),
                {
                    "core_server1"     : "logs/config/logging.configuration.server1.txt",
                    "laboratory1" : "logs/config/logging.configuration.laboratory1.txt",
                },
                before_shutdown,
                (
                     Launcher.FileNotifier("_file_notifier", "server started"),
                ),
                pid_file = 'weblab.pid',
                waiting_port = 10012,
                debugger_ports = { 
                     'core_server1' : 10013, 
                }
            )

    launcher.launch()
except:
    import traceback
    traceback.print_exc()
    raise
