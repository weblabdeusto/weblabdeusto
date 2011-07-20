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
import xmlrpclib

import weblab.experiment.Experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged
from voodoo.threaded import threaded

DEFAULT_LABVIEW_WIDTH   = "1000"
DEFAULT_LABVIEW_HEIGHT  = "800"
DEFAULT_LABVIEW_VERSION_PROPERTY = "2010"
DEFAULT_LABVIEW_SERVER_PROPERTY = "http://www.weblab.deusto.es:5906/"
DEFAULT_LABVIEW_VINAME_PROPERTY = "BlinkLED.vi"
DEFAULT_LABVIEW_VI_DIRECTORY_PROPERTY = r"."
DEFAULT_LABVIEW_SEND_FILE = False

MODE_HTML   = 'html'     # Generating the <object> etc.
MODE_IFRAME = 'iframe' # Pointing to the labview html page

DEFAULT_LABVIEW_MODE = MODE_HTML

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
        self.initialize_t = None
        self.clean_initialize_t = None

        self.filename   = self._cfg_manager.get_value("labview_filename")
        self.server_url = self._cfg_manager.get_value("labview_server",  DEFAULT_LABVIEW_SERVER_PROPERTY)
        self.viname     = self._cfg_manager.get_value("labview_viname",  DEFAULT_LABVIEW_VINAME_PROPERTY)
        self.version    = self._cfg_manager.get_value("labview_version", DEFAULT_LABVIEW_VERSION_PROPERTY)
        self.width      = self._cfg_manager.get_value("labview_width",   DEFAULT_LABVIEW_WIDTH)
        self.height     = self._cfg_manager.get_value("labview_height",  DEFAULT_LABVIEW_HEIGHT)
        self.must_wait  = self._cfg_manager.get_value("labview_must_wait", True)
        self.mode       = self._cfg_manager.get_value("labview_mode",    DEFAULT_LABVIEW_MODE)
        self.send_file  = self._cfg_manager.get_value("labview_send_file", DEFAULT_LABVIEW_SEND_FILE)

        if self.send_file:
            self.fpga_url   = self._cfg_manager.get_value("labview_fpga_url")
        
        if self.mode == MODE_IFRAME:
            self.vi_url = self._cfg_manager.get_value("labview_vi_url")
        elif self.mode == MODE_HTML:
            pass
        else:
            raise Exception("Mode not supported")

        if not self.version in LV_VERSIONS:
            raise Exception("Unsupported LabVIEW provided version: %s. Add the proper arguments to weblab/experiment/experiments/labview_experiment/LabViewExperiment.py" % self.version)

        self.copyfile   = self._cfg_manager.get_value("labview_copyfile", False)
        self.opened     = False
        self.cpfilename = self._cfg_manager.get_value("labview_copyfilename", None)
        self.directory = self._cfg_manager.get_value("labview_vi_directory", DEFAULT_LABVIEW_VI_DIRECTORY_PROPERTY)
        self.vi_path = self.directory + os.sep + self.viname
        if self.copyfile:
            if not self.viname.endswith(".vi"):
                raise Exception("The VI file does not end by .vi ('%s'), so the experiment code would be broken" % self.viname)
            if not os.path.exists(self.directory):
                raise Exception("Provided directory where the experiment should be does not exist: %s" % self.directory)
            if not os.path.exists(self.vi_path):
                raise Exception("Provided vi full path does not exist: %s" % self.vi_path)

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self):
        cur_initialize_t = self.initialize_t
        if cur_initialize_t is not None and cur_initialize_t.isAlive():
            cur_initialize_t.join()

        cur_clean_initialize_t = slef.clean_initialize_t
        if cur_clean_initialize_t is not None and cur_clean_initialize_t.isAlive():
            cur_clean_initialize_t.join()

        if self.send_file:
            self.initialize_t = self.initialize()
            self.clean_initialize_t = None
        else:
            self.initialize_t = None
            self.clean_initialize_t = self.clean_initialize()

    @threaded
    def initialize(self):
        if self.must_wait:
            self.wait_for(self.filename, 'close')

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
        else:
            if self.cpfilename is not None:
                open(self.cpfilename,'w').write(self.vi_path)
            

        print "Opening file..."
        self.open_file(self.filename)
        print "Opened"
        self.opened = True
        return ""

    @threaded
    def clean_initialize(self):
        if self.must_wait:
            self.wait_for(self.filename, 'close')

    def wait_for(self, filename, message_to_avoid):
        MAX_TIME = 20 # seconds
        STEP_TIME = 0.05
        MAX_STEPS = MAX_TIME / STEP_TIME
        counter = 0
        print "Waiting for ready in file '%s'... " % filename
        while os.path.exists(filename) and self.current_content(filename) == message_to_avoid and counter < MAX_STEPS:
            print "The file exists, and its content is %s and therefore I wait" % message_to_avoid
            time.sleep(0.05)
            counter += 1

        if counter == MAX_STEPS:
            raise Exception("LabView experiment: Time waiting for 'ready' content in file '%s' exceeded (max %s seconds)" % (filename, MAX_TIME))       

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        if command == 'is_open':
            # First wait for the thread to finish
            if self.initialize_t is None or self.initialize_t.isAlive():
                return "no"

            # Then check the result
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
            if self.mode == MODE_IFRAME:
                return """
                <iframe src="%s" height="%s" width="%s" scroll="yes"/>
                """ % (self.vi_url, self.height, self.width)
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
            html += "<OBJECT ID=\"LabVIEWControl\" CLASSID=\"" + classId + "\" WIDTH=" + str(self.width) + " HEIGHT=" + str(self.height) + " CODEBASE=\"" + codeBase + "\">\n"
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
        if self.send_file:
            # If the cleaning process is still running, wait for it
            cur_clean_initialize_t = self.clean_initialize_t
            if cur_clean_initialize_t is not None:
                cur_clean_initialize_t.join()

            # Then program the FPGA
            response = xmlrpclib.Server(self.fpga_url).program(content)

            # Start initializing the system
            self.initialize_t = self.initialize()

            return response
        return "NOP"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        print "Disposing"

        cur_initialize_t = self.initialize_t
        if cur_initialize_t is not None and cur_initialize_t.isAlive():
            print "Waiting for the initialization to finish"
            cur_initialize_t.join()

        print "Real finishing"
        if self.opened:
            print "Closing file"
            self.close_file(self.filename)
            self.opened = False
            print "Closed"
            counter = 0
            time_to_wait = 10 # seconds
            time_step = 0.1
            max_counter = time_to_wait / time_step
            while self.current_content() == 'close' and counter < max_counter:
                time.sleep(time_step)
        if self.copyfile:
            time.sleep(2)
            print "Removing %s" % self.new_path
            try:
                os.remove(self.new_path)
            except:
                import traceback
                traceback.print_exc()
            print "Removed"
        return "Disposing"

    def current_content(self, filename = None):
        if filename is None:
            fname = self.filename
        else:
            fname = filename
        return open(fname).read().strip().lower()

    def open_file(self, filename):
        self.write_to_file(filename, 'Open')

    def close_file(self, filename):
        self.write_to_file(filename, 'Close')

    def write_to_file(self, filename, content):
        open(filename,'w').write(content)
        

