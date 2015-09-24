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

import unittest
import mocker
import weblab.experiment.devices.vm.manager as VirtualMachineManager

import voodoo.configuration as ConfigurationManager
import test.unit.configuration as configuration_module

class VirtualMachineManagerTestCase(mocker.MockerTestCase):
                
    def setUp(self):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        self.vmm = VirtualMachineManager.VirtualMachineManager(cfg_manager)

    def tearDown(self):
        pass
    
    def test_copy_file(self):
        pass
        

        
def suite():
    return unittest.makeSuite(VirtualMachineManagerTestCase)

if __name__ == '__main__':
    unittest.main()
