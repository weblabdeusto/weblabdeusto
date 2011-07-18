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
DEFAULT_LABVIEW_VERSION_PROPERTY = "2010"
DEFAULT_LABVIEW_SERVER_PROPERTY = "http://www.weblab.deusto.es:5906/"
DEFAULT_LABVIEW_VINAME_PROPERTY = "BlinkLED.vi"
DEFAULT_LABVIEW_VI_DIRECTORY_PROPERTY = r"."

CLASSID     = "classid"
CODEBASE    = "codebase"
PLUGINSPAGE = "pluginspage"

LV_VERSIONS = {
    "2009" : {
        CLASSID       : "CLSID:A40B0AD4-B50E-4E58-8A1D-8544233807B1",
        CODEBASE      : "ftp://ftp.ni.com/support/labview/runtime/windows/9.0/LVRTE90min.exe",
        PLUGINSPAGE   : "http://digital.ni.com/express.nsf/bycode/exck2m",
    },
    "2010" : {
        CLASSID       : "CLSID:A40B0AD4-B50E-4E58-8A1D-8544233807B2",
        CODEBASE      : "ftp://ftp.ni.com/support/labview/runtime/windows/2010/LVRTE2010min.exe",
        PLUGINSPAGE   : "http://digital.ni.com/express.nsf/bycode/exck2m",
    }
}

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

        if not self.version in LV_VERSIONS:
            raise Exception("Unsupported LabVIEW provided version: %s. Add the proper arguments to weblab/experiment/experiments/labview_experiment/LabViewExperiment.py" % self.version)

        self.copyfile   = self._cfg_manager.get_value("labview_copyfile", True)
        self.opened     = False
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
                print "The file exists, and its content is close and therefore I wait"
                time.sleep(0.05)
                counter += 1

            if counter == MAX_STEPS:
                raise Exception("LabView experiment: Time waiting for 'ready' content in file '%s' exceeded (max %s seconds)" % (self.filename, MAX_TIME))
        print "Ready found or file did not exist. Starting..."

        if self.copyfile:
            print "Generating code..."
            code = str(random.randint(1000,1000000))
            self.new_path   = self.vi_path[:-3] + code + ".vi"
            self.new_viname = self.viname[:-3] + code + ".vi"
            print "Copying file"
            print "Copying %s to %s" % (self.vi_path, self.new_path)
                
            shutil.copy(self.vi_path, self.new_path)
            print "Writing into %s this %s" % (self.cpfilename, self.new_path)
            open(self.cpfilename,'w').write(self.new_path)

        print "Opening file..."
        self.open_file(self.filename)
        self.opened = True
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
        if command == 'get_html':
            if self.copyfile:
                viname = self.new_viname
            else:
                viname = self.viname

            version = LV_VERSIONS[self.version]
            classId     = version[CLASSID]
            codeBase    = version[CODEBASE]
            pluginsPage = version[PLUGINSPAGE]
            control     = "true"
            
            html = ""
            html += "<OBJECT ID=\"LabVIEWControl\" CLASSID=\"" + classId + "\" WIDTH=" + str(self.width) + " HEIGHT=" + str(self.width) + " CODEBASE=\"" + codeBase + "\">\n"
            html += "<PARAM name=\"server\" value=\"" + self.server_url + "\">\n"
            html += "<PARAM name=\"LVFPPVINAME\" value=\"" + viname + "\">\n"
            html += "<PARAM name=\"REQCTRL\" value=" + control + ">\n"
            html += "<EMBED SRC=\"" + self.server_url + viname + "\" LVFPPVINAME=\"" + viname + "\" REQCTRL=" + control + " TYPE=\"application/x-labviewrpvi90\" WIDTH=" + str(self.width) + " HEIGHT=" + str(self.height) + " PLUGINSPAGE=\"" + pluginsPage + "\">\n"
            html += "</EMBED>\n"
            html += "</OBJECT>\n"
            return html

        return "cmd_not_supported"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        return "NOP"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        print "Disposing"
        if self.opened:
            self.close_file(self.filename)
            self.opened = False
        if self.copyfile:
            try:
                os.remove(self.new_path)
            except:
                import traceback
                traceback.print_exc()
        return "Disposing"

    def current_content(self):
        return open(self.filename).read().strip().lower()

    def open_file(self, filename):
        self.write_to_file(filename, 'Open')

    def close_file(self, filename):
        self.write_to_file(filename, 'Close')

    def write_to_file(self, filename, content):
        open(filename,'w').write(content)
        

