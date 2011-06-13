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

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self):
        print "Starting"
        self.open_file(self.filename)
        return "Starting"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
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

    def open_file(self, filename):
        self.write_to_file(filename, 'Open')

    def close_file(self, filename):
        self.write_to_file(filename, 'Close')

    def write_to_file(self, filename, content):
        open(filename,'w').write(content)
        

