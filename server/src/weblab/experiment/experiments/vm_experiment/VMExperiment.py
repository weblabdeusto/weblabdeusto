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

import uuid
import random
import shutil
from voodoo.threaded import *
from weblab.experiment.devices.vm import *

DEBUG = True

CFG_FILE_COPY_SRC = "vm_file_copy_origin"
CFG_FILE_COPY_DST = "vm_file_copy_target"
CFG_URL = "vm_url"
CFG_VM_TYPE = "vm_vm_type"
CFG_SHOULD_STORE_IMAGE = "vm_should_store_image"

DEFAULT_FILE_COPY_SRC = "c:/orig.txt"
DEFAULT_FILE_COPY_DST = "c:/target.txt"
DEFAULT_URL = "rdp://localhost:6667"
DEFAULT_VM_TYPE = "VirtualBox"
DEFAULT_SHOULD_STORE_IMAGE = True


class VMExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VMExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_base_config()
        self.session_id = None
        self.vm = self.find_vm_manager(self.vm_type)(self._cfg_manager) # Instance the appropriate VM manager
        self.is_ready = False
        
    def read_base_config(self):
        """
        Reads the base config parameters from the config file. More parameters will be read through
        the same manager from the actual Virtual Machine Manager, and some may be implementation-specific.
        """
        self.file_copy_src = self._cfg_manager.get_value(CFG_FILE_COPY_SRC, DEFAULT_FILE_COPY_SRC)
        self.file_copy_dst = self._cfg_manager.get_value(CFG_FILE_COPY_DST, DEFAULT_FILE_COPY_DST)
        self.url = self._cfg_manager.get_value(CFG_URL, DEFAULT_URL)
        self.vm_type = self._cfg_manager.get_value(CFG_VM_TYPE, DEFAULT_VM_TYPE)
        self.should_store_image = self._cfg_manager.get_value(CFG_SHOULD_STORE_IMAGE, DEFAULT_SHOULD_STORE_IMAGE)

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        """
        Callback run when the experiment is started
        """
        self.handle_start_exp_t()
        return "Ok"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if command == "get_configuration":
            self.url
        elif command == "is_ready":
            if self.is_ready: return "1"
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
        self.handle_dispose_t()
        return "Ok"
    

    @threaded()
    def handle_start_exp_t(self):
        self.session_id = self.generate_session_id()
        self.vm._copy_file(self.file_copy_src, self.file_copy_src)
        self.vm.launch_vm()
        self.setup()
        self.is_ready = True
        
    @threaded()
    def handle_dispose_t(self):
        self.is_ready = False
        self.vm.kill_vm()
        if( self.should_store_image ):
            self.vm.store_image()
        
    def setup(self):
        # TODO Implement this
        pass
    
    def generate_session_id(self):
        """ 
        Generates and returns a unique id
        """
        id = uuid.uuid1()
        idstr = id.get_hex()
        return idstr
    
    def find_vm_manager(self, name):
        """
        Returns the class of the VM manager with the specified name.
        """
        subclasses = VirtualMachineManager.VirtualMachineManager.__subclasses__()
        for sc in subclasses:
            if sc.__name__ == name:
                return sc
        raise Exception("Could not find an implementation for the specified VM")
        
        
    

