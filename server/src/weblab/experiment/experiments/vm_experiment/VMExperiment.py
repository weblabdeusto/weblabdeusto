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
# Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
# 

import weblab.experiment.Experiment as Experiment

from voodoo.override import Override

import random


DEBUG = True


class VMExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VMExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_config()
        
    def read_config(self):
        """
        Reads the config parameters from the config file (such as the
        measurement server address)
        """
        pass

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        """
        Callback run when the experiment is started
        """
        return "Ok"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if command == "get_configuration":
            return "udp://localhost:8000/whatever"
        elif command == "is_ready":
            n = random.randint(0, 15)
            if n == 0: return "1"
            return "0"
            
        return "Ok"

        

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        """ 
        Callback for when the client sends a file to the experiment
        server. Currently unused for this experiment, should never get 
        called.
        """
        if(DEBUG):
            print "[VMExperiment] do_send_file_to_device called"
        return "Ok"


    @Override(Experiment.Experiment)
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if(DEBUG):
            print "[VMExperiment] do_dispose called"
        return "Ok"

