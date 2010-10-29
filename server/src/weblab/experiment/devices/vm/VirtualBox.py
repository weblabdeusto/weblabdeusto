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
#         Pablo Orduña <pablo@ordunya.com>
# 

import subprocess

from VirtualMachineManager import VirtualMachineManager
from voodoo.override import Override

VBOXMANAGE_COMMAND_NAME  = 'vboxmanage_command'
VBOXMANAGE_COMMAND_DEFAULT_VALUE = 'VBoxManage' # Could be something like r'c:\Program Files\VirtualBox\VBoxManage' or similar

VBOX_VM_NAME = 'vbox_vm_name'
VBOX_VM_DEFAULT_VALUE = 'weblab'

class VirtualBox(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)

        self.vboxmanage     = cfg_manager.get_value(VBOXMANAGE_COMMAND_NAME, VBOXMANAGE_COMMAND_DEFAULT_VALUE)
        self.vm_name        = cfg_manager.get_value(VBOX_VM_NAME, VBOX_VM_DEFAULT_VALUE)

    @Override(VirtualMachineManager)
    def launch_vm(self):
        process = subprocess.Popen([self.vboxmanage,'-startvm',self.vm_name])
        process.wait()
    
    @Override(VirtualMachineManager)
    def kill_vm(self):
        process = subprocess.Popen([self.vboxmanage,'controlvm',self.vm_name,'poweroff'])
        process.wait()
            
    @Override(VirtualMachineManager)
    def is_alive_vm(self):
        process = subprocess.Popen([self.vboxmanage,'-q','list','runningvms'], stdout=subprocess.PIPE)
        process.wait()
        return self.vm_name in [ line.split('"')[0] for line in process.stdout.readlines() ]
    

