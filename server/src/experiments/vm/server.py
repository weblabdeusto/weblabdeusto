#!/usr/bin/python
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
# Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
# 

import weblab.experiment.experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged
import voodoo.log as log

import uuid

import time

from voodoo.threaded import threaded

# Those imports are required for the experiment to locate the config-specified classes dynamically.
# It is known which classes to bring into the namespace through the __init__'s __all__
import weblab.experiment.devices.vm.manager as VirtualMachineManager
import experiments.vm.user_manager.manager as UserManager

DEBUG = False
DEBUG_NOT_PREPARE = False

CFG_URL = "vm_url"
CFG_VM_TYPE = "vm_vm_type"
CFG_USER_MANAGER_TYPE = "vm_user_manager_type"
CFG_SHOULD_STORE_IMAGE = "vm_should_store_image"
CFG_ESTIMATED_LOAD_TIME = "vm_estimated_load_time"

# TODO: Consider adding this to the config
PWD_LENGTH = 8

DEFAULT_URL = "rdp://localhost:6667"
DEFAULT_VM_TYPE = "VirtualMachineDummy"
DEFAULT_USER_MANAGER_TYPE = "DummyUserManager"
DEFAULT_SHOULD_STORE_IMAGE = True
DEFAULT_ESTIMATED_LOAD_TIME = 15

TIME_WAITING_START = 10

class VMExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VMExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_base_config() # Read those vars which are NOT vm implementation specific.
        self.session_id = None
        self.vm = self.find_vm_manager(self.vm_type)(self._cfg_manager) # Instance the appropriate VM manager
        self.user_manager_class = self.find_user_manager(self.user_manager_type) # Instance the appropiate user manager
        self.user_manager = None
        self.is_ready = False # Indicate whether the machine is ready to be used
        self.is_error = False # Indicate whether we are in an error state
        self.error = None # The error
        self._start_t = None
        self._dispose_t = None
        
    def read_base_config(self):
        """
        Reads the base config parameters from the config file. More parameters will be read through
        the same manager from the actual Virtual Machine Manager, and some may be implementation-specific.
        """
        self.url = self._cfg_manager.get_value(CFG_URL, DEFAULT_URL)
        self.vm_type = self._cfg_manager.get_value(CFG_VM_TYPE, DEFAULT_VM_TYPE)
        self.user_manager_type = self._cfg_manager.get_value(CFG_USER_MANAGER_TYPE, DEFAULT_USER_MANAGER_TYPE)
        self.should_store_image = self._cfg_manager.get_value(CFG_SHOULD_STORE_IMAGE, DEFAULT_SHOULD_STORE_IMAGE)
        self.estimated_load_time = self._cfg_manager.get_value(CFG_ESTIMATED_LOAD_TIME, DEFAULT_ESTIMATED_LOAD_TIME)
        
    @Override(Experiment.Experiment)
    @logged("info")
    def do_get_api(self):
        return "1"


    @logged("info")
    @Override(Experiment.Experiment)
    def do_start_experiment(self, *args, **kwargs):
        """
        Callback run when the experiment is started. After the starting
        thread finishes successfully, it will set is_ready to True.
        """
        # Using temporal variable "um" so if somebody does self.user_manager = None 
        # between the "if self.user_manager is not None" and the action there is no error
        um = self.user_manager
        if um is not None:
            um.cancel()

        initial = time.time()
        while self.is_ready and (initial + TIME_WAITING_START) > time.time():
            if DEBUG:
                print "is_ready:",self.is_ready
            time.sleep(0.1)

        if self.is_ready:
            return "Already started and ready"

        if self.is_error:
            return "Can't start. Error state: ", str(self.error)

        if self._start_t != None and self._start_t.isAlive():
            return "Already starting"

        self.session_id = self.generate_session_id()
        self._start_t = self.handle_start_exp_t()
        return "Starting"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        
        # Returns the URL to access the VM. The VM itself is not necessarily ready for access yet.
        if command == "get_configuration":
            return self.url + "     with password: " + self.session_id
            
        # Returns 1 if the client should be able to connect to the VM already, 
        # 0;<estimated_load_time> if it isn't ready yet,
        # 3;<error msg> if an error occurred
        elif command == "is_ready":
            if self.is_ready: return "1"    # 1:Ready
            if self.is_error: return "3;%s" % str(self.error)
            return "0;%s" % self.estimated_load_time
        
        elif command == "is_alive":
            if not self.is_ready: return "0"
            if self.vm.is_alive_vm(): return "1"
            return "0"
            
        return "cmd_not_supported"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        """ 
        Callback for when the client sends a file to the experiment
        server. Currently unused for this experiment, should never get 
        called.
        """
        if(DEBUG):
            print "[VMExperiment] do_send_file_to_device called"
        return "NOP"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        self.handle_dispose()
        return "Disposing"
    

    @threaded()
    def handle_start_exp_t(self):
        """
        Executed on a work thread, will prepare the VM for use, and unless an exception is raised, 
        will not return until it's fully ready (and then it will set the is_ready attribute). 
        """
        if DEBUG:
            print "t_starting"
        self.ensure_vm_not_started()
        # Avoid preparing the VM, just for specific debugging purposes. Probably this condition should eventually be removed.
        if not DEBUG_NOT_PREPARE:
            self.vm.prepare_vm()
        if DEBUG:
            print "t_prepared"
            print type(self.vm)
            print self.vm_type
        self.vm.launch_vm()
        if DEBUG:
            print "t_launched"
        self.setup()
        if DEBUG:
            print "t_setup"
        if self.is_error == True:
            self.is_ready = False
        else:
            self.is_ready = True
    
    def ensure_vm_not_started(self):
        """
        Though it should never happen, this function makes sure that the VM is not already
        running, which would prevent proper initialization.
        """
        if DEBUG:
            print "ensure_vm_not_started"
        start_time = time.time()
        while self.vm.is_alive_vm():
            if DEBUG:
                print "VM is alive. Killing..."
            self.vm.kill_vm()
            elapsed = time.time() - start_time
            if elapsed > 20:
                raise Exception("It was not possible to ensure that the machine is powered off")
        
    #TODO: Consider whether this should indeed be threaded, and in that case, consider what would happen
    # if an experiment was started with this function still running, after dispose has returned.
    #@threaded()
    def handle_dispose(self):
        """
        Executed on a work thread, will handle clean-up.
        """
        if self.user_manager is not None:
            self.user_manager.cancel()
        self.vm.kill_vm()
        if( self.should_store_image ):
            self.vm.store_image()

        self.is_ready = False
        self.error = None
        self.is_error = False
        self._start_t = None
        self.user_manager = None

    def load_user_manager(self):
        self.user_manager = self.user_manager_class(self._cfg_manager)
        
    def setup(self):
        """ Configures the VM """
        self.load_user_manager()
        try:
            self.user_manager.configure(self.session_id)
            if DEBUG:
                print "t_configured"
        except Exception as ex:
            self.error = str(ex)
            self.is_error = True

            log.log(
                VMExperiment,
                log.level.Error,
                "Error configuring user manager: %s" % ex
            )
            log.log_exc(
                VMExperiment,
                log.level.Warning
            )
                

    
    def generate_session_id(self):
        """ Generates and returns a unique id """
        """ TODO: Use SessionGenerator """
        id = uuid.uuid1()
        idstr = id.get_hex()[:PWD_LENGTH]
        return idstr
    
    def find_user_manager(self, name):
        """
        Returns the class of the User Manager with the specified name.
        @param name __name__ of the class (not the fully qualified one)
        """
        subclasses = UserManager.UserManager.__subclasses__()
        for sc in subclasses:
            if sc.__name__ == name:
                return sc
        raise Exception("""Could not find an implementation for the specified User Manager. Make sure the
            class name specified is not the fully-qualified one, and that it is present in the module's
            __all__ list.""") 
        
    
    def find_vm_manager(self, name):
        """
        Returns the class of the VM manager with the specified name.
        @param name __name__ of the class (not the fully qualified one)
        """
        subclasses = VirtualMachineManager.VirtualMachineManager.__subclasses__()
        for sc in subclasses:
            if sc.__name__ == name:
                return sc
        raise Exception("""Could not find an implementation for the specified VM. Make sure the
            class name specified is not the fully-qualified one, and that it is present in the module's
            __all__ list.""")
        
        
    

