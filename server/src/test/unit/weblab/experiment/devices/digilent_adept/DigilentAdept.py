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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 
import unittest


import test.unit.configuration as configuration_module

import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.experiment.devices.digilent_adept.DigilentAdept as DigilentAdept
import weblab.exceptions.experiment.devices.digilent_adept.DigilentAdeptExceptions as DigilentAdeptExceptions

class DigilentAdeptTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self._device = DigilentAdept.DigilentAdept(self.cfg_manager)

    def test_program_device(self):
        self._device.program_device("ok.svf")

    def test_program_device_errors(self):
        self.assertRaises(
            DigilentAdeptExceptions.ProgrammingGotErrors,
            self._device.program_device,
            "error.svf"
        )
        self.assertRaises(
            DigilentAdeptExceptions.ProgrammingGotErrors,
            self._device.program_device,
            "return-1.svf"
        )
                
        self._device._busy = True
        self.assertRaises(
            DigilentAdeptExceptions.AlreadyProgrammingDeviceException,
            self._device.program_device,
            "ok.svf"
        )
        self._device._busy = False

        self.cfg_manager._values['digilent_adept_full_path'] = ['p0wn3d']

        self.assertRaises(
            DigilentAdeptExceptions.ErrorProgrammingDeviceException,
            self._device.program_device,
            "ok.svf"
        )
        self.cfg_manager._values.pop('digilent_adept_full_path')
                
        self.assertRaises(
            DigilentAdeptExceptions.CantFindDigilentAdeptProperty,
            self._device.program_device,
            "ok.svf"
        )
        self.cfg_manager.reload()

def suite():
    return unittest.makeSuite(DigilentAdeptTestCase)

if __name__ == '__main__':
    unittest.main()
