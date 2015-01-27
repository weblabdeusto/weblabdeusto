#!/usr/bin/env python
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

from abc import ABCMeta, abstractmethod
import os
import sys

base_dir = os.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-3])
sys.path.append(base_dir)

import time
import signal
import threading
import subprocess
import socket

import logging.config

import voodoo.counter as counter
import voodoo.process_starter as process_starter
import voodoo.gen.loader.ServerLoader as ServerLoader
import voodoo.gen.loader.ConfigurationParser as ConfigurationParser
import voodoo.rt_debugger as rt_debugger

##########################################################
#                                                        #
#  EventWait and different implementations:              #
#                                                        #
#  They get blocked until a certain condition (decided   #
#  by the child class)                                   #
#                                                        #
##########################################################

class EventWait(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def wait(self):
        pass

class _WaitingSignal(object):
    def __init__(self, signal_wait):
        super(_WaitingSignal, self).__init__()
        self.signal_wait = signal_wait

    def signal_handle(self, signum, arg):
        self.signal_wait._notify()

class SignalWait(EventWait):
    def __init__(self, signal_code = None):
        super(SignalWait, self).__init__()
        if signal_code == None:
            self.signal = signal.SIGTERM
        else:
            self.signal = signal_code
        self.ev = threading.Event()
        waiting_signal = _WaitingSignal(self)
        signal.signal(self.signal, waiting_signal.signal_handle)

    def wait(self):
        while not self.ev.isSet():
            self.ev.wait(0.1)

    def _notify(self):
        self.ev.set()

DEFAULT_MESSAGE = 'Press <enter> to finish...\n'

class RawInputWait(EventWait):
    def __init__(self, message = DEFAULT_MESSAGE):
        super(RawInputWait, self).__init__()
        self.message = message
    def wait(self):
        raw_input(self.message)

class TimeWait(EventWait):
    def __init__(self, seconds):
        super(TimeWait, self).__init__()
        self.seconds = seconds
    def wait(self):
        time.sleep(self.seconds)

class SocketWait(EventWait):
    def __init__(self, port):
        super(SocketNotifier, self).__init__()
        self.port = port

    def wait(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.s.bind(('localhost', self.port))
        self.s.listen(5)
        self.s.accept()
        self.s.close()

class EventNotifier(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def notify(self):
        pass

class FileNotifier(EventNotifier):
    def __init__(self, filepath, message):
        super(FileNotifier, self).__init__()
        self.message  = message
        self.filepath = filepath

    def notify(self):
        of = open(self.filepath, 'w')
        of.write(self.message)
        of.flush()
        of.close()

    def dispose(self):
        os.remove(self.filepath)

class SocketNotifier(EventNotifier):
    def __init__(self, host, port):
        super(SocketNotifier, self).__init__()
        self.host = host
        self.port = port

    def notify(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.send("finished")

    def dispose(self):
        self.s.close()

# We could add SignalNotifier, etc. etc.

###################
#                 #
# Launcher object #
#                 #
###################

class EventWaitHolder(threading.Thread):
    def __init__(self, event_waiter, event):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("EventWaitHolder"))
        self.event_waiter = event_waiter
        self.event        = event

    def run(self):
        self.event_waiter.wait()
        self.event.set()

class AbstractLauncher(object):
    def __init__(self,
                    config_dir, machine_name,
                    event_waiters, logging_file_config,
                    before_finish_callback = None, event_notifiers = None):

        super(AbstractLauncher, self).__init__()

        self.config_dir             = config_dir
        self.machine_name           = machine_name
        self.event_waiters          = event_waiters
        self.logging_file_config    = logging_file_config
        self.before_finish_callback = before_finish_callback
        self.event_notifiers        = event_notifiers

    def notify(self):
        if self.event_notifiers is not None:
            for event_notifier in self.event_notifiers:
                event_notifier.notify()

    def dispose_notifiers(self):
        if self.event_notifiers is not None:
            for event_notifier in self.event_notifiers:
                event_notifier.dispose()

    def wait(self):
        holders = []
        ev  = threading.Event()

        for event_waiter in self.event_waiters:
            ewh = EventWaitHolder(event_waiter, ev)
            ewh.setDaemon(True)
            ewh.start()
            holders.append(ewh)

        if len(self.event_waiters) > 0:
            while not ev.isSet():
                ev.wait(0.1)

    def notify_and_wait(self):
        self.notify()

        try:
            self.wait()
        finally:
            self.dispose_notifiers()

        rt_debugger.stop_debugger() # Even if it has not been initialized

        if self.before_finish_callback is not None:
            self.before_finish_callback()

class Launcher(AbstractLauncher):
    def __init__(self,
                    config_dir, machine_name, instance_name,
                    event_waiters, logging_file_config,
                    before_finish_callback = None, event_notifiers = None):
        super(Launcher, self).__init__(
                    config_dir, machine_name,
                    event_waiters, logging_file_config,
                    before_finish_callback, event_notifiers
                )
        self.instance_name          = instance_name

    def launch(self):
        logging.config.fileConfig(
                self.logging_file_config
            )

        server_loader = ServerLoader.ServerLoader()
        instance_handler = server_loader.load_instance(
                self.config_dir,
                self.machine_name,
                self.instance_name
            )
        try:
            self.notify_and_wait()
        finally:
            instance_handler.stop()

class MachineLauncher(AbstractLauncher):
    def __init__(self,
            config_dir, machine_name,
            event_waiters, logging_file_config,
            before_finish_callback = None, event_notifiers = None,
            pid_file = None, waiting_port = 54321, debugger_ports = None):
        super(MachineLauncher, self).__init__(
                    config_dir, machine_name,
                    event_waiters, logging_file_config,
                    before_finish_callback, event_notifiers
                )
        self.waiting_port   = waiting_port
        self.debugger_ports = debugger_ports
        if pid_file is not None:
            mypid = str(os.getpid())
            open(pid_file, 'w').write(mypid)

    def _create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.socket.bind(('',self.waiting_port))
        self.socket.listen(5)

    def _wait_for_process_to_start(self):
        self.socket.accept()

    def launch(self):
        global_parser = ConfigurationParser.GlobalParser()
        global_configuration = global_parser.parse(self.config_dir)
        machine_configuration = global_configuration.machines.get(self.machine_name)
        if machine_configuration is None:
            raise Exception("Machine %s not found" % self.machine_name)

        self._create_socket()

        processes = []
        for instance_name in machine_configuration.instances:
            instance_config = machine_configuration.instances[instance_name]
            if isinstance(self.logging_file_config, dict):
                logging_file_config = self.logging_file_config[instance_name]
            else:
                logging_file_config = self.logging_file_config
            if self.debugger_ports is None:
                debugger_port = "None"
            else:
                debugger_port = self.debugger_ports.get(instance_name, "None")
            args = (
                        "python",
                        "-OO",
                        __file__,
                        self.config_dir,
                        self.machine_name, instance_name,
                        logging_file_config,
                        str(self.waiting_port),
                        str(debugger_port)
                    )
            subprocess_kargs = dict(
                    args = args,
                    stdin = subprocess.PIPE
                )
            process = process_starter.start_process(instance_config.user, (), subprocess_kargs)
            processes.append(process)

        self.notify_and_wait()

        for process in processes:
            try:
                process.stdin.write("\n")
            except:
                pass

        self.wait_for_subprocesses(processes)

        if len(processes) > 0:
            for process in processes:
                process.terminate()

        self.wait_for_subprocesses(processes)

        if len(processes) > 0:
            for process in processes:
                process.kill()

        self.wait_for_subprocesses(processes)

    def wait_for_subprocesses(self, processes):
        for _ in xrange(20):
            dead_processes = []
            for process in processes:
                try:
                    return_code = process.poll()
                except:
                    dead_processes.append(process)
                else:
                    if return_code is not None:
                        dead_processes.append(process)
            for process in dead_processes:
                processes.remove(process)
            if len(processes) == 0:
                break
            else:
                time.sleep(0.05)

def kill_launcher(pid_file):
    pid = int(open(pid_file).read())
    os.kill(pid, signal.SIGTERM)

if __name__ == '__main__':
    if len(sys.argv) != 7:
        print >> sys.stderr, "Error: invalid number of arguments"
        sys.exit(-1)

    _, config_dir, machine_name, instance_name, logging_file, waiting_port, debugger_port = sys.argv
    waiters = (RawInputWait(""),)
    notifiers = (SocketNotifier("localhost", int(waiting_port)),)
    if debugger_port != "None":
        rt_debugger.launch_debugger(int(debugger_port))
    launcher = Launcher(config_dir, machine_name, instance_name, waiters, logging_file, event_notifiers = notifiers)
    launcher.launch()

