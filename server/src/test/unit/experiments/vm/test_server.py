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

import time
import unittest
import mocker
import test.unit.configuration as configuration_module

import voodoo.configuration as ConfigurationManager

import experiments.vm.server as VMExperiment
import experiments.vm.user_manager as user_manager
import weblab.experiment.devices.vm.dummy as VirtualMachineDummy

from weblab.experiment.devices.vm.manager import VirtualMachineManager
from experiments.vm.user_manager.manager import UserManager

from voodoo.override import Override

class TestPermanentConfigError(user_manager.UserManager.PermanentConfigureError):
    pass

class TestTempConfigError(user_manager.UserManager.TemporaryConfigureError):
    pass

class TestUserManager(UserManager):
    
    def __init__(self, cfg_manager):
            self.cfg = cfg_manager
            self.except_to_raise = None
            self.configure_called = 0
    
    def configure(self, sid):
        self.configure_called += 1
        if self.except_to_raise is not None:
            raise self.except_to_raise
        
def create_wrapped_vmexp(user_manager):
    class WrappedVMExperiment(VMExperiment.VMExperiment):
        def load_user_manager(self):
            self.user_manager = user_manager
    return WrappedVMExperiment

class TestVirtualMachine(VirtualMachineManager):
    
    def __init__(self, cfg_manager):
        VirtualMachineManager.__init__(self, cfg_manager)
        self.running = False
        self.launched = False
        self.prepared = False
    

    @Override(VirtualMachineManager)
    def launch_vm(self):
        if not self.prepared:
            pass
        else:
            self.launched = True
    
    @Override(VirtualMachineManager)
    def kill_vm(self):
        self.running = False
        self.launched = False     
        self.prepared = False
             
    @Override(VirtualMachineManager)
    def store_image_vm(self):
        pass
    
    @Override(VirtualMachineManager)
    def is_alive_vm(self):
        pass
    
    @Override(VirtualMachineManager)
    def prepare_vm(self):
            self.prepared = True

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
        vmexp.load_user_manager()
        um = vmexp.user_manager
        self.assertIs(type(vm), VirtualMachineDummy.VirtualMachineDummy)
        self.assertIs(type(um), user_manager.DummyUserManager.DummyUserManager)
        self.assertFalse(vmexp.is_ready)
        self.assertFalse(vmexp.is_error)
        
    
    def test_init(self):
        """ Tests the ctor, using config-specified variables """
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        
        vmexp = VMExperiment.VMExperiment(None, None, cfg_manager)
        
        self.assertNotEqual(vmexp.url, None)
        self.assertTrue(vmexp.url.__contains__("127.0.0.1"))
        self.assertFalse(vmexp.should_store_image)
        self.assertEqual(vmexp.vm_type, "TestVirtualMachine")
        self.assertEqual(vmexp.user_manager_type, "TestUserManager")
        
        vm = vmexp.vm
        vmexp.load_user_manager()
        um = vmexp.user_manager
        self.assertIs(type(vm), TestVirtualMachine)
        self.assertIs(type(um), TestUserManager)
        self.assertFalse(vmexp.is_ready)
        self.assertFalse(vmexp.is_error)
    
    
    def test_generate_session_id(self):
        
        cfg_manager = ConfigurationManager.ConfigurationManager()
        vmexp = VMExperiment.VMExperiment(None, None, cfg_manager)
        
        l = []
        s = set()
        for i in range(100): #@UnusedVariable
            id = vmexp.generate_session_id()
            self.assertNotEqual(id, None)
            l.append(id)
            s.add(id)
            
        # Make sure the ids generated were unique
        self.assertEqual(len(l), len(s))

    
    def test_standard_process(self):
        VMExperiment.TIME_WAITING_START = 0.2
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
       
        um = TestUserManager(cfg_manager)
        WrappedVMExperiment = create_wrapped_vmexp(um)
        vmexp = WrappedVMExperiment(None, None, cfg_manager) 
        
        vm = vmexp.vm
    
        ret = vmexp.do_start_experiment("{}","{}")
        self.assertEqual("Starting", ret)
        
        initial_time = time.time()
        while um.configure_called == 0:
            time.sleep(0.01)
            now = time.time()
            if now - initial_time > 2:
                self.fail("Waiting too long for start thread to run")
    
        # Check that if we try again, it doesn't handle it the same way, but rather
        # tells us that it's already started or that it is still starting.    
        ret = vmexp.do_start_experiment("{}","{}")
        self.assertTrue( ret.__contains__("Already") )
        
        initial_time = time.time()
        # Wait until it is ready
        while not vmexp.is_ready and not vmexp.is_error:
            time.sleep(0.01)
            now = time.time()
            if now - initial_time > 10:
                self.fail("Waiting too long for vmexp")
        
        self.assertTrue(vm.launched)
        
        self.assertTrue(um.configure_called > 0)
        
        
        ret = vmexp.do_dispose()
        self.assertEqual("Disposing", ret)
        
        if vmexp._dispose_t is not None:
            vmexp._dispose_t.join(10)
            if vmexp._dispose_t.isAlive():
                self.fail("Dispose thread still alive after long timeout")
        
        self.assertFalse(vm.launched)
        self.assertFalse(vm.prepared)
        self.assertFalse(vm.running)


    def test_config_permanent_raise(self):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        um = TestUserManager(cfg_manager)

        WrappedVMExperiment = create_wrapped_vmexp(um)
        vmexp = WrappedVMExperiment(None, None, cfg_manager) 
        
        vm = vmexp.vm
        
        excep = TestPermanentConfigError()
        um.except_to_raise = excep
        
        vmexp.do_start_experiment("{}","{}")
    
        initial_time = time.time()
        # Wait until it is ready
        while not vmexp.is_ready and not vmexp.is_error:
            time.sleep(0.01)
            now = time.time()
            if now - initial_time > 10:
                self.fail("Waiting too long for vmexp")
    
        self.assertTrue(vmexp.error != None)
        self.assertTrue(vmexp.is_error)
        self.assertFalse(vmexp.is_ready)
        self.assertIs(type(vmexp.error), TestPermanentConfigError)
    
        vmexp.do_dispose()
        
        if vmexp._dispose_t is not None:
            vmexp._dispose_t.join(10)
            if vmexp._dispose_t.isAlive():
                self.fail("Dispose thread still alive after long timeout")
        
        self.assertFalse(vm.launched)
        self.assertFalse(vm.prepared)
        self.assertFalse(vm.running)
        
        
def suite():
    return unittest.makeSuite(VMExperimentTestCase)

if __name__ == '__main__':
    unittest.main()
