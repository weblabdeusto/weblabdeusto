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

import unittest
import mocker
import test.unit.configuration as configuration_module

import weblab.experiment.Util as ExperimentUtil
import voodoo.configuration.ConfigurationManager as ConfigurationManager
import weblab.experiment.experiments.vm_experiment.VMExperiment as VMExperiment
import weblab.experiment.experiments.vm_experiment.user_manager as user_manager
import weblab.experiment.devices.vm.VirtualMachineDummy as VirtualMachineDummy

from weblab.experiment.devices.vm.VirtualMachineManager import VirtualMachineManager
from voodoo.override import Override


class TestVirtualMachine(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)
        self.running = False
        self.launched = False
        self.prepared = False
    

    @Override(VirtualMachineManager)
    def launch_vm(self):
        print "wut"
        if not self.prepared:
            print "VM has not been prepared"
        else:
            print "VM has been launched."
            self.launched = True
    
    @Override(VirtualMachineManager)
    def kill_vm(self):
        print "VM has been killed."
        self.running = False
        self.launched = False     
        self.prepared = False
             
    @Override(VirtualMachineManager)
    def store_image_vm(self):
        print "Storing VM image"
    
    @Override(VirtualMachineManager)
    def is_alive_vm(self):
        print "Checking whether it is alive"
        return self.running
    
    @Override(VirtualMachineManager)
    def prepare_vm(self):
            self.prepared = True
            print "VM is now prepared."

class VMExperimentTestCase(mocker.MockerTestCase):
                
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_default_config(self):
        """ Tests that the ctor works and sets proper defaults with a blank configuration manager."""
        cfg_manager = ConfigurationManager.ConfigurationManager()
        
        vmexp = VMExperiment.VMExperiment(None, None, cfg_manager)
        
        self.assertNotEqual(vmexp.url, None)
        self.assertTrue(vmexp.url.__contains__("localhost"))
        self.assertTrue(vmexp.should_store_image, True)
        self.assertEqual(vmexp.vm_type, "VirtualMachineDummy")
        self.assertEqual(vmexp.user_manager_type, "DummyUserManager")
        
        vm = vmexp.vm
        um = vmexp.user_manager
        self.assertIs(type(vm), VirtualMachineDummy.VirtualMachineDummy)
        self.assertIs(type(um), user_manager.DummyUserManager.DummyUserManager)
        self.assertFalse(vmexp.is_ready)
        self.assertFalse(vmexp.is_error)
        
    
    def test_init(self):
        """ Tests the ctor, using config-specified variables """
        print "VERSION: ", __import__("sys").version_info
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        
        vmexp = VMExperiment.VMExperiment(None, None, cfg_manager)
        
        self.assertNotEqual(vmexp.url, None)
        self.assertTrue(vmexp.url.__contains__("127.0.0.1"))
        self.assertFalse(vmexp.should_store_image)
        self.assertEqual(vmexp.vm_type, "TestVirtualMachine")
        self.assertEqual(vmexp.user_manager_type, "DummyUserManager")
        
        vm = vmexp.vm
        um = vmexp.user_manager
        self.assertIs(type(vm), TestVirtualMachine)
        self.assertIs(type(um), user_manager.DummyUserManager.DummyUserManager)
        self.assertFalse(vmexp.is_ready)
        self.assertFalse(vmexp.is_error)
    
    
    def test_generate_session_id(self):
        
        cfg_manager = ConfigurationManager.ConfigurationManager()
        vmexp = VMExperiment.VMExperiment(None, None, cfg_manager)
        
        l = []
        s = set()
        for i in range(100):
            id = vmexp.generate_session_id()
            self.assertNotEqual(id, None)
            l.append(id)
            s.add(id)
            
        # Make sure the ids generated were unique
        self.assertEqual(len(l), len(s))

    
    def test_do_start_experiment(self):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        
        vmexp = VMExperiment.VMExperiment(None, None, cfg_manager) 
        
        vm = vmexp.vm
        um = vmexp.user_manager
    
        ret = vmexp.do_start_experiment()   
        self.assertEqual("Starting", ret)
    
        # Check that if we try again, it doesn't handle it the same way, but rather
        # tells us that it's already started or that it is still starting.    
        ret = vmexp.do_start_experiment()
        self.assertTrue( ret.__contains__("Already") )
        
        # Wait until it is ready
        while not vmexp.is_ready:
            pass    # TODO: Consider Sleep()'ing here, or setting a timeout
        
        self.assertTrue(vm.launched)
        
        # TODO: Check whether it was prepared properly through a custom UserManager.
        
        ret = vmexp.do_dispose()
        self.assertEqual("Disposing", ret)
        
        while vmexp._dispose_t.isAlive():
            pass
        
        self.assertFalse(vm.launched)
        self.assertFalse(vm.prepared)
        self.assertFalse(vm.running)
        
def suite():
    return unittest.makeSuite(VMExperimentTestCase)

if __name__ == '__main__':
    unittest.main()