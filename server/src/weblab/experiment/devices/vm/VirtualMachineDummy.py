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
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

from VirtualMachineManager import VirtualMachineManager
from voodoo.override import Override

class VirtualMachineDummy(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)
        self.running = False
        self.launched = False
    
    @Override(VirtualMachineManager)
    def launch_vm(self):
        print "VM has been launched."
        self.launched = True
    
    @Override(VirtualMachineManager)
    def kill_vm(self):
        print "VM has been killed."
        self.running = False
        self.launched = False     
             
    @Override(VirtualMachineManager)
    def store_image_vm(self):
        print "Storing VM image"
    
    @Override(VirtualMachineManager)
    def is_alive_vm(self):
        print "Checking whether it is alive"
        return self.running
    
    @Override(VirtualMachineManager)
    def prepare_vm(self):
        if(not self.launched):
            print "Error: VM currently not launched"
        else:
            self.running = True
            print "VM is now running."
        
    
    