#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

from WebLabDeustoExperimentServer import ExperimentServer, Launcher


class DummyExperimentServer(ExperimentServer):
    
    def start_experiment(self):
        print "start_experiment"
        return "ok"
        
    def send_file(self, content, file_info):
        print "send_file"
        return "ok"
        
    def send_command(self, command_string):
        print "send_command"
        return "ok"
    
    def dispose(self):
        print "dispose"
        return "ok"
    
    # Optional:
    def is_up_and_running(self):
        return False
        

launcher = Launcher(12345, DummyExperimentServer())
launcher.start()