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

class VirtualBox(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)
    
    @Override(VirtualMachineManager)
    def launch_vm(self):
        pass
    
    @Override(VirtualMachineManager)
    def kill_vm(self):
        pass
             
    @Override(VirtualMachineManager)
    def store_image_vm(self):
        pass
    
    @Override(VirtualMachineManager)
    def is_alive_vm(self):
        pass
    
    @Override(VirtualMachineManager)
    def prepare_vm(self):
        pass
    
