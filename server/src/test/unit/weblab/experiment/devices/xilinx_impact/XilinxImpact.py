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
# 
import unittest


import test.unit.configuration as configuration_module

import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.experiment.devices.xilinx_impact.XilinxImpact as XilinxImpact
import weblab.exceptions.experiment.devices.xilinx_impact.XilinxImpactExceptions as XilinxImpactExceptions

class XilinxImpactTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

    def _test_xilinx_impact(self, xilinx_impact):
        xilinx_impact.program_device("hello world")

        self.assertRaises(
            XilinxImpactExceptions.ProgrammingGotErrors,
            xilinx_impact.program_device,
            "show error"
        )
        self.assertRaises(
            XilinxImpactExceptions.ProgrammingGotErrors,
            xilinx_impact.program_device,
            "show stderr"
        )
        self.assertRaises(
            XilinxImpactExceptions.ProgrammingGotErrors,
            xilinx_impact.program_device,
            "return -1"
        )

    def test_normal(self):
        self._test_xilinx_impact(XilinxImpact.XilinxImpactFPGA(self.cfg_manager))
        self._test_xilinx_impact(XilinxImpact.XilinxImpactPLD(self.cfg_manager))

    def test_errors(self):
        impact = XilinxImpact.XilinxImpactFPGA(self.cfg_manager)
        impact._busy = True
        self.assertRaises(
            XilinxImpactExceptions.AlreadyProgrammingDeviceException,
            impact.program_device,
            "foo"
        )
        impact._busy = False

        self.cfg_manager._values['xilinx_impact_full_path'] = ['p0wn3d']

        self.assertRaises(
            XilinxImpactExceptions.ErrorProgrammingDeviceException,
            impact.program_device,
            "bar"
        )
        self.cfg_manager._values.pop('xilinx_impact_full_path')
                
        self.assertRaises(
            XilinxImpactExceptions.CantFindXilinxProperty,
            impact.program_device,
            "bar"
        )
        self.cfg_manager.reload()


def suite():
    return unittest.makeSuite(XilinxImpactTestCase)

if __name__ == '__main__':
    unittest.main()

