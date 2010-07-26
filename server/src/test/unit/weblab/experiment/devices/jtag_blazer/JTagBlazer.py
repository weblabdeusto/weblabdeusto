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
# Author: Pablo Orduña <pablo@ordunya.com>
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 
import unittest


import test.unit.configuration as configuration_module

import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.experiment.devices.jtag_blazer.JTagBlazer as JTagBlazer
import weblab.exceptions.experiment.devices.jtag_blazer.JTagBlazerExceptions as JTagBlazerExceptions

class JTagBlazerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self._jtag_blazer_fpga = JTagBlazer.JTagBlazerFPGA(self.cfg_manager)
        self._jtag_blazer_pld = JTagBlazer.JTagBlazerPLD(self.cfg_manager)

    def test_program_device_ok(self):
        self._jtag_blazer_fpga.program_device("everything_ok.svf")
        self._jtag_blazer_pld.program_device("everything_ok.svf")
        
    def test_program_device_errors(self):
        self._test_program_device_errors(self._jtag_blazer_fpga)
        self._test_program_device_errors(self._jtag_blazer_pld)
        
    def _test_program_device_errors(self, jtag_blazer):
        self.assertRaises(
            JTagBlazerExceptions.InvalidSvfFileExtException,
            jtag_blazer.program_device,
            "file.svfxxx"
        )
        
        self.assertRaises(
            JTagBlazerExceptions.JTagBlazerSvf2JsvfErrorException,
            jtag_blazer.program_device,
            "svf2jsvf_error.svf"
        )
        
        self.assertRaises(
            JTagBlazerExceptions.JTagBlazerSvf2JsvfErrorException,
            jtag_blazer.program_device,
            "svf2jsvf_stderr.svf"
        )
        
        self.assertRaises(
            JTagBlazerExceptions.JTagBlazerSvf2JsvfErrorException,
            jtag_blazer.program_device,
            "svf2jsvf_return-1.svf"
        )    
        
        self.assertRaises(
            JTagBlazerExceptions.JTagBlazerTargetErrorException,
            jtag_blazer.program_device,
            "target_error.svf"
        )
        
        self.assertRaises(
            JTagBlazerExceptions.JTagBlazerTargetErrorException,
            jtag_blazer.program_device,
            "target_stderr.svf"
        )
        
        self.assertRaises(
            JTagBlazerExceptions.JTagBlazerTargetErrorException,
            jtag_blazer.program_device,
            "target_return-1.svf"
        )    
    
        jtag_blazer._busy = True
        self.assertRaises(
            JTagBlazerExceptions.AlreadyProgrammingDeviceException,
            jtag_blazer.program_device,
            "file.svf"
        )
        jtag_blazer._busy = False

        self.cfg_manager._values['xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path'] = ['p0wn3d']
        self.assertRaises(
            JTagBlazerExceptions.ErrorProgrammingDeviceException,
            jtag_blazer.program_device,
            "file.svf"
        )
        
        self.cfg_manager._values.pop('xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path')
        self.assertRaises(
            JTagBlazerExceptions.CantFindJTagBlazerProperty,
            jtag_blazer.program_device,
            "file.svf"
        )
        self.cfg_manager.reload()

        self.cfg_manager._values['xilinx_jtag_blazer_jbmanager_target_full_path'] = ['p0wn3d']
        self.assertRaises(
            JTagBlazerExceptions.ErrorProgrammingDeviceException,
            jtag_blazer.program_device,
            "file.svf"
        )
        
        self.cfg_manager._values.pop('xilinx_jtag_blazer_jbmanager_target_full_path')
        self.assertRaises(
            JTagBlazerExceptions.CantFindJTagBlazerProperty,
            jtag_blazer.program_device,
            "file.svf"
        )
        self.cfg_manager.reload()


def suite():
    return unittest.makeSuite(JTagBlazerTestCase)

if __name__ == '__main__':
    unittest.main()