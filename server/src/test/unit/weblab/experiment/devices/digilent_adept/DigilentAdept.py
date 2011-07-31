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

from mock import patch
import unittest

from voodoo.configuration.ConfigurationManager import ConfigurationManager
from weblab.experiment.devices.digilent_adept.DigilentAdept import DigilentAdept
import test.unit.configuration as configuration_module
import weblab.exceptions.experiment.devices.digilent_adept.DigilentAdeptExceptions as DigilentAdeptExceptions


class DigilentAdeptTestCase(unittest.TestCase):

    def setUp(self):
        cfg_manager = ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        self.device = DigilentAdept(cfg_manager)

    @patch('subprocess.Popen')
    def test_program_device(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = ''
        popen.stderr.read.return_value = ''

        self.device.program_device("file.svf")

    @patch('subprocess.Popen')
    def test_program_device_error_in_stdout(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = 'ERROR: bla bla bla'
        popen.stderr.read.return_value = ''

        self.assertRaises(
            DigilentAdeptExceptions.ProgrammingGotErrors,
            self.device.program_device,
            "file.svf"
        )

    @patch('subprocess.Popen')
    def test_program_device_error_in_exit(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = -1
        popen.stdout.read.return_value = ''
        popen.stderr.read.return_value = ''

        self.assertRaises(
            DigilentAdeptExceptions.ProgrammingGotErrors,
            self.device.program_device,
            "file.svf"
        )

    def test_program_device_already_programming(self):
        self.device._busy = True

        self.assertRaises(
            DigilentAdeptExceptions.AlreadyProgrammingDeviceException,
            self.device.program_device,
            "file.svf"
        )
        self.device._busy = False

    @patch('subprocess.Popen')
    def test_program_device_wrong_call(self, Popen):
        Popen.side_effect = Exception("can't create Popen!")

        self.assertRaises(
            DigilentAdeptExceptions.ErrorProgrammingDeviceException,
            self.device.program_device,
            "file.svf"
        )

    def test_program_device_wrong_config(self):
        self.device._cfg_manager._values.pop('digilent_adept_full_path')

        self.assertRaises(
            DigilentAdeptExceptions.CantFindDigilentAdeptProperty,
            self.device.program_device,
            "ok.svf"
        )


def suite():
    return unittest.makeSuite(DigilentAdeptTestCase)

if __name__ == '__main__':
    unittest.main()
