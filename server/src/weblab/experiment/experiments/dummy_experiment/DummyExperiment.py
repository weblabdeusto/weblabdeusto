#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
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

import time

import weblab.experiment.experiments.ud_xilinx_experiment.UdXilinxExperiment as UdXilinxExperiment

from voodoo.override import Override

class FakeImpact(object):
    def __init__(self):
        super(FakeImpact,self).__init__()
        self.clear()
    def program_device(self, program_path):
        print "FakeImpact::program_device: ", program_path
        try:
            self._paths.append(open(program_path).read())
        except Exception, e:
            print "I tried to show the program but i couldn't: ", e
        nseconds = 2
        print "Waiting %s seconds (simulating 'programming device...')" % nseconds
        time.sleep(nseconds)
        print "%i seconds have passed" % nseconds
        #raise Exception("A common exception")
    def get_suffix(self):
        return "whatever"
        
    def clear(self):
        self._paths = []

class FakeSerialPort(object):
    def __init__(self):
        super(FakeSerialPort,self).__init__()
        self.clear()
    def open_serial_port(self, number):
        print "FakeSerialPort::open_serial_port:", number
        self.dict['open'].append((self.cycle, number))
        self.cycle += 1
    def send_code(self, n):
        print "FakeSerialPort::send_code: ", n
        self.dict['send'].append((self.cycle, n))
        self.cycle += 1
    def close_serial_port(self):
        print "FakeSerialPort::close_serial_port: "
        self.dict['close'].append((self.cycle, None))
        self.cycle += 1
    def clear(self):
        self.dict = {'open':[], 'close':[], 'send' : []}
        self.cycle = 0

class DummyExperiment(UdXilinxExperiment.UdXilinxExperiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(DummyExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)

        self._xilinx_impact                 = FakeImpact()
        self._command_sender._serial_port   = FakeSerialPort()

    @Override(UdXilinxExperiment.UdXilinxExperiment)
    def do_dispose(self):
        print "Experiment disposed"
        return ""

    @Override(UdXilinxExperiment.UdXilinxExperiment)
    def do_start_experiment(self, *args, **kwargs):
        print "Experiment started", args, kwargs
        return '{ "initial_configuration" : "hi, from dummy experiment" }'

    @Override(UdXilinxExperiment.UdXilinxExperiment)
    def do_send_command_to_device(self, command):
        msg = "Received command: %s" % command
        print msg
        super(DummyExperiment, self).do_send_command_to_device(command)
        return msg

    @Override(UdXilinxExperiment.UdXilinxExperiment)
    def do_send_file_to_device(self, content, file_info):
        msg = "Received file with len: %s and file_info: %s" % (len(content), file_info)
        print msg
        return msg

