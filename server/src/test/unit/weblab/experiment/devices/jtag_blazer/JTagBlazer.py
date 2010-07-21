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

    def _test_jtag_blazer(self, jtag_blazer):
        jtag_blazer.program_device("hello world")

        self.assertRaises(
            JTagBlazerExceptions.ProgrammingGotErrors,
            jtag_blazer.program_device,
            "show error"
        )
        self.assertRaises(
            JTagBlazerExceptions.ProgrammingGotErrors,
            jtag_blazer.program_device,
            "show stderr"
        )
        self.assertRaises(
            JTagBlazerExceptions.ProgrammingGotErrors,
            jtag_blazer.program_device,
            "return -1"
        )

    def test_normal(self):
        self._test_jtag_blazer(JTagBlazer.JTagBlazerFPGA(self.cfg_manager))
        self._test_jtag_blazer(JTagBlazer.JTagBlazerPLD(self.cfg_manager))

    def test_errors(self):
        jtag_blazer = JTagBlazer.JTagBlazerFPGA(self.cfg_manager)
        jtag_blazer._busy = True
        self.assertRaises(
            JTagBlazerExceptions.AlreadyProgrammingDeviceException,
            jtag_blazer.program_device,
            "foo"
        )
        jtag_blazer._busy = False

        self.cfg_manager._values['jtag_blazer_xilinx_impact_full_path'] = ['p0wn3d']

        self.assertRaises(
            JTagBlazerExceptions.ErrorProgrammingDeviceException,
            jtag_blazer.program_device,
            "bar"
        )
        self.cfg_manager._values.pop('jtag_blazer_xilinx_impact_full_path')
                
        self.assertRaises(
            JTagBlazerExceptions.CantFindJTagBlazerProperty,
            jtag_blazer.program_device,
            "bar"
        )
        self.cfg_manager.reload()


def suite():
    return unittest.makeSuite(JTagBlazerTestCase)

if __name__ == '__main__':
    unittest.main()