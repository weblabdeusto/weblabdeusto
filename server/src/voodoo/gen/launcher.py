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
from __future__ import print_function, unicode_literals

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
import voodoo.rt_debugger as rt_debugger

# Can't locally import (from . import load_dir) since we're executing this file
from voodoo.gen import load_dir

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

class ConditionWait(EventWait):
    def __init__(self, condition = None):
        super(ConditionWait, self).__init__()
        if condition:
            self.condition = condition
        else:
            self.condition = threading.Condition()
    def wait(self):
        with self.condition:
            self.condition.wait()

class TimeWait(EventWait):
    def __init__(self, seconds):
        super(TimeWait, self).__init__()
        self.seconds = seconds
    def wait(self):
        time.sleep(self.seconds)

class SocketWait(EventWait):
    def __init__(self, port):
        super(SocketWait, self).__init__()
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

class ConditionNotifier(EventNotifier):
    def __init__(self, condition = None):
        super(ConditionNotifier, self).__init__()
        if condition:
            self.condition = condition
        else:
            self.condition = threading.Condition()
    def notify(self):
        with self.condition:
            self.condition.notify()

    def dispose(self):
        pass

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
                    config_dir, host_name,
                    event_waiters, logging_file_config,
                    before_finish_callback = None, event_notifiers = None):

        super(AbstractLauncher, self).__init__()

        self.config_dir             = config_dir
        self.host_name           = host_name
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
                    config_dir, host_name, process_name,
                    event_waiters, logging_file_config,
                    before_finish_callback = None, event_notifiers = ()):
        super(Launcher, self).__init__(
                    config_dir, host_name,
                    event_waiters, logging_file_config,
                    before_finish_callback, event_notifiers
                )
        self.process_name          = process_name

    def launch(self):
        logging.config.fileConfig(
                self.logging_file_config
            )

        global_config = load_dir(self.config_dir)
        process_handler = global_config.load_process(self.host_name, self.process_name)
        try:
            self.notify_and_wait()
        finally:
            process_handler.stop()

class HostLauncher(AbstractLauncher):
    def __init__(self,
            config_dir, host_name,
            event_waiters, logging_file_config,
            before_finish_callback = None, event_notifiers = None,
            pid_file = None, waiting_port = 54321, debugger_ports = None):
        super(HostLauncher, self).__init__(
                    config_dir, host_name,
                    event_waiters, logging_file_config,
                    before_finish_callback, event_notifiers
                )
        self.debugger_ports = debugger_ports
        if pid_file is not None:
            mypid = str(os.getpid())
            open(pid_file, 'w').write(mypid)

    def launch(self):
        global_configuration = load_dir(self.config_dir)
        host_configuration = global_configuration.get(self.host_name)
        if host_configuration is None:
            raise Exception("Machine %s not found" % self.host_name)

        os_processes = []
        for process_name in host_configuration:
            if isinstance(self.logging_file_config, dict):
                logging_file_config = self.logging_file_config[process_name]
            else:
                logging_file_config = self.logging_file_config
            if self.debugger_ports is None:
                debugger_port = "None"
            else:
                debugger_port = self.debugger_ports.get(process_name, "None")
            args = (
                        sys.executable,
                        "-OO",
                        __file__,
                        self.config_dir,
                        self.host_name, 
                        process_name,
                        logging_file_config,
                        str(debugger_port)
                    )
            subprocess_kargs = dict(
                    args = args,
                    stdin = subprocess.PIPE
                )

            os_process = process_starter.start_process((), subprocess_kargs)
            os_processes.append(os_process)

        self.notify_and_wait()

        if len(os_processes) > 0:
            for os_process in os_processes:
                try:
                    os_process.terminate()
                except:
                    pass

        self.wait_for_subprocesses(os_processes)

        if len(os_processes) > 0:
            for os_process in os_processes:
                os_process.kill()

        self.wait_for_subprocesses(os_processes)

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

# In the past, HostLauncher was called MachineLauncher. 
# We keep this for compatiblity reasons
MachineLauncher = HostLauncher

def kill_launcher(pid_file):
    pid = int(open(pid_file).read())
    os.kill(pid, signal.SIGTERM)

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Error: invalid number of arguments", file=sys.stderr)
        sys.exit(-1)

    _, config_dir, host_name, process_name, logging_file, debugger_port = sys.argv
    waiters = (SignalWait(),)
    if debugger_port != "None":
        rt_debugger.launch_debugger(int(debugger_port))
    launcher = Launcher(config_dir, host_name, process_name, waiters, logging_file)
    launcher.launch()

