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
# Author: Pablo Orduña <pablo.orduna@deusto.es>
# 

import os
import time

import weblab.experiment.Experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged


DEFAULT_LABVIEW_WIDTH = "1000"
DEFAULT_LABVIEW_HEIGHT = "800"
DEFAULT_LABVIEW_URL_PROPERTY = "http://www.weblab.deusto.es:5906/testone/BlinkLED.html"

class LabViewExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(LabViewExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.filename = self._cfg_manager.get_value("labview_filename")
        self.url      = self._cfg_manager.get_value("labview_url", DEFAULT_LABVIEW_URL_PROPERTY)
        self.width    = self._cfg_manager.get_value("labview_width", DEFAULT_LABVIEW_WIDTH)
        self.height   = self._cfg_manager.get_value("labview_height", DEFAULT_LABVIEW_HEIGHT)
        self.must_wait = self._cfg_manager.get_value("labview_must_wait", True)

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self):
        if self.must_wait:
            MAX_TIME = 12 # seconds
            STEP_TIME = 0.05
            MAX_STEPS = MAX_TIME / STEP_TIME
            counter = 0
            print "Waiting for ready in file '%s'... " % self.filename
            while os.path.exists(self.filename) and self.current_content() == 'close' and counter < MAX_STEPS:
                time.sleep(0.05)
                counter += 1

            if counter == MAX_STEPS:
                raise Exception("LabView experiment: Time waiting for 'ready' content in file '%s' exceeded (max %s seconds)" % (self.filename, MAX_TIME))
        print "Ready found or file did not exist. Starting..."
        self.open_file(self.filename)
        return ""

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        if command == 'is_open':
            if not self.must_wait or self.current_content() == 'opened':
                return "yes"
            return "no"
        if command == 'get_url':
            return '%s;%s;%s' % (self.height, self.width, self.url)
        return "cmd_not_supported"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        return "NOP"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        print "Disposing"
        self.close_file(self.filename)
        return "Disposing"

    def current_content(self):
        return open(self.filename).read().strip().lower()

    def open_file(self, filename):
        self.write_to_file(filename, 'Open')

    def close_file(self, filename):
        self.write_to_file(filename, 'Close')

    def write_to_file(self, filename, content):
        open(filename,'w').write(content)
        

