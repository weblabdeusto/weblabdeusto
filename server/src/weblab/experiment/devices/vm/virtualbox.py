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
#         Pablo Orduña <pablo@ordunya.com>
# 
from __future__ import print_function, unicode_literals

import sys
import subprocess

from voodoo.log import logged
import voodoo.log as log

from weblab.experiment.devices.vm.manager import VirtualMachineManager
from voodoo.override import Override

DEBUG = True

VBOXMANAGE_COMMAND_NAME  = 'vboxmanage_command'
VBOXMANAGE_COMMAND_DEFAULT_VALUE = 'VBoxManage' # Could be something like r'c:\Program Files\VirtualBox\VBoxManage' or similar

VBOXHEADLESS_COMMAND_NAME  = 'vboxheadless_command'
VBOXHEADLESS_COMMAND_DEFAULT_VALUE = 'VBoxHeadless' # Could be something like r'c:\Program Files\VirtualBox\VBoxHeadless' or similar

VBOXHEADLESS_START_OPTIONS = 'vboxheadless_start_options'
VBOXHEADLESS_START_OPTIONS_DEFAULT_VALUE = []

VBOX_VM_NAME = 'vbox_vm_name'
VBOX_VM_DEFAULT_VALUE = 'weblab'
VBOX_VM_BASE_SNAPSHOT = 'vbox_base_snapshot'
VBOX_VM_DEFAULT_BASE_SNAPSHOT = 'Ready'



# Note: These functions make use of the VBoxManage utility, which comes with VirtualBox
# It should hence be accessible. Under windows, it will often have to be added to the PATH
# environment variable.

class VirtualBox(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)

        self.vboxmanage       = cfg_manager.get_value(VBOXMANAGE_COMMAND_NAME, VBOXMANAGE_COMMAND_DEFAULT_VALUE)
        self.vboxheadless     = cfg_manager.get_value(VBOXHEADLESS_COMMAND_NAME, VBOXHEADLESS_COMMAND_DEFAULT_VALUE)
        self.vm_name          = cfg_manager.get_value(VBOX_VM_NAME, VBOX_VM_DEFAULT_VALUE)
        self.vm_base_snapshot = cfg_manager.get_value(VBOX_VM_BASE_SNAPSHOT, VBOX_VM_DEFAULT_BASE_SNAPSHOT)
        self.vboxheadless_start_options = cfg_manager.get_value(VBOXHEADLESS_START_OPTIONS, VBOXHEADLESS_START_OPTIONS_DEFAULT_VALUE)

    @Override(VirtualMachineManager)
    @logged('info')
    def launch_vm(self):
        """
        Launches the VirtualMachine. Does not wait until the virtual OS is ready. It is hence
        possible, and likely, for this function to return a relatively long time before
        the Virtual Machine is truly ready for usage.
        """
        self._print("Starting VM")
        options = [self.vboxheadless,'-startvm',self.vm_name]
        options.extend(self.vboxheadless_start_options)
        self.popen = subprocess.Popen(options)
#        result = process.wait()
        result = "(other thread)"
        self._print("Started %s" % result)
    
    @Override(VirtualMachineManager)
    @logged('info')
    def kill_vm(self):
        self._print("Killing VM")
        process = subprocess.Popen([self.vboxmanage,'controlvm',self.vm_name,'poweroff'])
        result = process.wait()
        self._print("Killed %s" % result)
            
    @Override(VirtualMachineManager)
    @logged('info')
    def is_alive_vm(self):
        self._print("listing vms")
        process = subprocess.Popen([self.vboxmanage,'-q','list','runningvms'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        lines = process.stdout.readlines()

        self._print("running: " + str(lines))

        running = [ line.split('"')[1] for line in lines if len(line.split('"')) > 1 and not line.startswith(' ') and not line.startswith('WARN') and not line.startswith('\t') ]

        self._print("Running parsed: %s" % running)

        return self.vm_name in running

    @Override(VirtualMachineManager)
    @logged('info')
    def prepare_vm(self):

        self._print("RESTORING %s FOR %s" % (self.vm_base_snapshot, self.vm_name))

        process = subprocess.Popen([self.vboxmanage, 'snapshot', self.vm_name, "restore", self.vm_base_snapshot])
        result = process.wait()

        self._print("RESTORED, RETURNED %s " % result)

    def _print(self, msg):
        log.log( VirtualBox, log.level.Info, msg)
        if DEBUG:
            print("WebLabVirtualBox::%s" % msg)
            sys.stdout.flush()
