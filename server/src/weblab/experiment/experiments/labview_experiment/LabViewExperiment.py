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
import shutil
import random

import weblab.experiment.Experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged


DEFAULT_LABVIEW_WIDTH   = "1000"
DEFAULT_LABVIEW_HEIGHT  = "800"
DEFAULT_LABVIEW_VERSION_PROPERTY = "2009"
DEFAULT_LABVIEW_SERVER_PROPERTY = "http://www.weblab.deusto.es:5906/"
DEFAULT_LABVIEW_VINAME_PROPERTY = "BlinkLED.vi"
DEFAULT_LABVIEW_VI_DIRECTORY_PROPERTY = r"."

class LabViewExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(LabViewExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.filename   = self._cfg_manager.get_value("labview_filename")
        self.server_url = self._cfg_manager.get_value("labview_server",  DEFAULT_LABVIEW_SERVER_PROPERTY)
        self.viname     = self._cfg_manager.get_value("labview_viname",  DEFAULT_LABVIEW_VINAME_PROPERTY)
        self.version    = self._cfg_manager.get_value("labview_version", DEFAULT_LABVIEW_VERSION_PROPERTY)
        self.width      = self._cfg_manager.get_value("labview_width",   DEFAULT_LABVIEW_WIDTH)
        self.height     = self._cfg_manager.get_value("labview_height",  DEFAULT_LABVIEW_HEIGHT)
        self.must_wait  = self._cfg_manager.get_value("labview_must_wait", True)

        self.copyfile   = self._cfg_manager.get_value("labview_copyfile", True)
        if self.copyfile:
            self.cpfilename = self._cfg_manager.get_value("labview_copyfilename")
            if not self.viname.endswith(".vi"):
                raise Exception("The VI file does not end by .vi ('%s'), so the experiment code would be broken" % self.viname)
            self.directory = self._cfg_manager.get_value("labview_vi_directory", DEFAULT_LABVIEW_VI_DIRECTORY_PROPERTY)
            if not os.path.exists(self.directory):
                raise Exception("Provided directory where the experiment should be does not exist: %s" % self.directory)
            self.vi_path = self.directory + os.sep + self.viname
            if not os.path.exists(self.vi_path):
                raise Exception("Provided vi full path does not exist: %s" % self.vi_path)

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

        if self.copyfile:
            code = str(random.randint(1000,1000000))
            self.new_path   = self.vi_path[:-3] + code + ".vi"
            self.new_viname = self.viname[:-3] + code + ".vi"
            shutil.copy(self.path, self.new_path)
            open(self.cpfilename,'w').write(self.new_path)

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
            if self.copyfile:
                viname = self.new_viname
            else:
                viname = self.viname
            return '%s;%s;%s;%s;%s' % (self.height, self.width, viname, self.server_url, self.version)
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
        if self.copyfile:
            os.remove(self.new_path)
        return "Disposing"

    def current_content(self):
        return open(self.filename).read().strip().lower()

    def open_file(self, filename):
        self.write_to_file(filename, 'Open')

    def close_file(self, filename):
        self.write_to_file(filename, 'Close')

    def write_to_file(self, filename, content):
        open(filename,'w').write(content)
        

