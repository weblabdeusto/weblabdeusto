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

import shutil

class VirtualMachineManager(object):
    
    def __init__(self, cfg_manager):
        self._cfg = cfg_manager
    
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
        pass
    
    def prepare_vm(self):
        """
        Prepares the Virtual Machine before using it, generally by copying the
        base HDD and / or memory files to the right place.
        """
        pass
    
    def _copy_file(self, src, dst):
        """ 
        Copies src into dst
        """
        shutil.copy(src, dst)
    
    
        