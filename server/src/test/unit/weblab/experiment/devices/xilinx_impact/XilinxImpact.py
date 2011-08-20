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

import weblab.experiment.devices.xilinx_impact.XilinxImpact as XilinxImpact
import weblab.experiment.devices.xilinx_impact.exc as XilinxImpactExceptions

class XilinxImpactTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self._fpga = XilinxImpact.XilinxImpactFPGA(self.cfg_manager)
        self._pld = XilinxImpact.XilinxImpactPLD(self.cfg_manager)

    def test_program_device(self):
        self._fpga.program_device("everything_ok.bit")
        self._pld.program_device("everything_ok.jed")

    def test_program_device_errors(self):
        self._test_program_device_errors(self._fpga)
        self._test_program_device_errors(self._pld)

    def _test_program_device_errors(self, impact):
        self.assertRaises(
            XilinxImpactExceptions.ProgrammingGotErrors,
            impact.program_device,
            "error.file"
        )
        self.assertRaises(
            XilinxImpactExceptions.ProgrammingGotErrors,
            impact.program_device,
            "stderr.file"
        )
        self.assertRaises(
            XilinxImpactExceptions.ProgrammingGotErrors,
            impact.program_device,
            "return-1.file"
        )
                
        impact._busy = True
        self.assertRaises(
            XilinxImpactExceptions.AlreadyProgrammingDeviceException,
            impact.program_device,
            "file.file"
        )
        impact._busy = False

        self.cfg_manager._values['xilinx_impact_full_path'] = ['p0wn3d']

        self.assertRaises(
            XilinxImpactExceptions.ErrorProgrammingDeviceException,
            impact.program_device,
            "file.file"
        )
        self.cfg_manager._values.pop('xilinx_impact_full_path')
                
        self.assertRaises(
            XilinxImpactExceptions.CantFindXilinxProperty,
            impact.program_device,
            "file.file"
        )
        self.cfg_manager.reload()
        
    def test_source2svf(self):
        self._fpga.source2svf("everything_ok.bit")
        self._pld.source2svf("everything_ok.jed")
        
    def test_source2svf_errors(self):
        self._test_source2svf_errors(self._fpga)
        self._test_source2svf_errors(self._pld)
        
    def _test_source2svf_errors(self, impact):
        self.assertRaises(
            XilinxImpactExceptions.GeneratingSvfFileGotErrors,
            impact.source2svf,
            "error.file"
        )
        self.assertRaises(
            XilinxImpactExceptions.GeneratingSvfFileGotErrors,
            impact.source2svf,
            "return-1.file"
        )

        self.cfg_manager._values['xilinx_impact_full_path'] = ['p0wn3d']

        self.assertRaises(
            XilinxImpactExceptions.ErrorProgrammingDeviceException,
            impact.source2svf,
            "file.file"
        )
        self.cfg_manager._values.pop('xilinx_impact_full_path')
                
        self.assertRaises(
            XilinxImpactExceptions.CantFindXilinxProperty,
            impact.source2svf,
            "file.file"
        )
        self.cfg_manager.reload()
        

def suite():
    return unittest.makeSuite(XilinxImpactTestCase)

if __name__ == '__main__':
    unittest.main()
