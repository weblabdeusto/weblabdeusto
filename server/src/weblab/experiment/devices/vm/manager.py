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
#         Pablo Orduña <pablo@ordunya.com>
# 
from __future__ import print_function, unicode_literals

import os
import shutil
import datetime

VM_DISKS_TO_SAVE_NAME          = 'vm_disks_to_save_name'
VM_DISKS_TO_SAVE_DEFAULT_VALUE = []

VM_STORAGE_DIR_NAME = "vm_storage_dir"
VM_STORAGE_DIR_DEFAULT_VALUE = "/tmp/"

VM_DISKS_TO_PREPARE_NAME = 'vm_prepare_name' # A dictionary like { '/home/nctrun/.virtualbox/image.vdi', '/usr/local/weblab/original_vms/image.vdi' }
VM_DISKS_TO_PREPARE_DEFAULT_VALUE = {}

class VirtualMachineManager(object):
    
    def __init__(self, cfg_manager):
        self._cfg = cfg_manager
        self.vm_disks     = cfg_manager.get_value(VM_DISKS_TO_SAVE_NAME,    VM_DISKS_TO_SAVE_DEFAULT_VALUE)
        self.vm_store_dir = cfg_manager.get_value(VM_STORAGE_DIR_NAME,      VM_STORAGE_DIR_DEFAULT_VALUE)
        self.vm_prepare   = cfg_manager.get_value(VM_DISKS_TO_PREPARE_NAME, VM_DISKS_TO_PREPARE_DEFAULT_VALUE)
    

    def launch_vm(self):
        """
        Launches the Virtual Machine. Might take some time before it's actually ready.
        """
        pass
    
    def kill_vm(self):
        """
        Kills the Virtual Machine.
        """
        pass
    
    def is_alive_vm(self):
        """
        Returns true if the Virtual Machine is ready to use, false otherwise.
        Should also return false if for any reason, it wasn't possible to check the machine's state.
        """
        pass
    
    def store_image_vm(self):
        """
        Saves the Virtual Machine's image.
        """
        identifier = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        for disk in self.vm_disks:
            dst = os.sep.join(self.vm_storage_dir, '%s_%s' % (identifier, disk.replace('/','_').replace(os.sep,'_')))
            self._copy_file(disk, dst)

    def prepare_vm(self):
        """
        Prepares the Virtual Machine before using it, generally by copying the
        base HDD and / or memory files to the right place.
        """
        for disk in self.vm_prepare:
            src = self.vm_prepare[disk]
            self._copy_file(src, disk)

    def _copy_file(self, src, dst):
        """ 
        Copies src into dst
        """
        shutil.copy(src, dst)
    
