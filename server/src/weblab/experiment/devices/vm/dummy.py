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
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 
from __future__ import print_function, unicode_literals

from weblab.experiment.devices.vm.manager import VirtualMachineManager
from voodoo.override import Override

class VirtualMachineDummy(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)
        self.running = False
        self.launched = False
        self.prepared = False
        self.error = False
        self.stored = False
    
    @Override(VirtualMachineManager)
    def launch_vm(self):
        if self.prepared and not self.running and not self.error:
            self.launched = True
        else:
            self.launched = False
    
    @Override(VirtualMachineManager)
    def kill_vm(self):
        self.running = False
        self.launched = False     
        self.prepared = False
             
    @Override(VirtualMachineManager)
    def store_image_vm(self):
        self.stored = True
    
    @Override(VirtualMachineManager)
    def is_alive_vm(self):
        return self.running
    
    @Override(VirtualMachineManager)
    def prepare_vm(self):
            self.prepared = True
        
    
