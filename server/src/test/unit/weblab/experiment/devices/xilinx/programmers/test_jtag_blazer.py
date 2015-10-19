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
# Author: Pablo Orduña <pablo@ordunya.com>
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

from mock import patch
import unittest

from voodoo.configuration import ConfigurationManager
from weblab.experiment.devices.xilinx.programmers import jtag_blazer
from test.util.fakeobjects import return_values
import test.unit.configuration as configuration_module


class JTagBlazerTestCase(unittest.TestCase):

    def setUp(self):
        cfg_manager = ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        self.jtag_blazer = jtag_blazer.JTagBlazer(cfg_manager)

    @patch('subprocess.Popen')
    def test_program_device_ok(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = ''
        popen.stderr.read.return_value = ''
        self.jtag_blazer.program_device("file.svf", "0.0.0.0")

    def test_program_device_invalid_svf(self):
        self.assertRaises(
            jtag_blazer.InvalidSvfFileExtError,
            self.jtag_blazer.program_device,
            "file.svfxxx", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_svf2jsvf_stdout_error(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = 'ERROR'
        popen.stderr.read.return_value = ''

        self.assertRaises(
            jtag_blazer.JTagBlazerSvf2JsvfErrorError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_svf2jsvf_stderr_error(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = ''
        popen.stderr.read.return_value = 'ERROR'

        self.assertRaises(
            jtag_blazer.JTagBlazerSvf2JsvfErrorError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_svf2jsvf_code_error(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = -1
        popen.stdout.read.return_value = ''
        popen.stderr.read.return_value = ''

        self.assertRaises(
            jtag_blazer.JTagBlazerSvf2JsvfErrorError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_target_stdout_error(self, Popen):
        popen = Popen.return_value
        popen.wait.side_effect = return_values([0, 0])
        popen.stdout.read.side_effect = return_values(['', 'ERROR'])
        popen.stderr.read.side_effect = return_values(['', ''])

        self.assertRaises(
            jtag_blazer.JTagBlazerTargetErrorError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_target_stderr_error(self, Popen):
        popen = Popen.return_value
        popen.wait.side_effect = return_values([0, 0])
        popen.stdout.read.side_effect = return_values(['', ''])
        popen.stderr.read.side_effect = return_values(['', 'ERROR'])

        self.assertRaises(
            jtag_blazer.JTagBlazerTargetErrorError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_target_code_error(self, Popen):
        popen = Popen.return_value
        popen.wait.side_effect = return_values([0, -1])
        popen.stdout.read.side_effect = return_values(['', ''])
        popen.stderr.read.side_effect = return_values(['', ''])

        self.assertRaises(
            jtag_blazer.JTagBlazerTargetErrorError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    @patch('subprocess.Popen')
    def test_program_device_already_programming(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = ''
        popen.stderr.read.return_value = ''
        self.jtag_blazer._busy = True

        self.assertRaises(
            jtag_blazer.AlreadyProgrammingDeviceError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )
        self.jtag_blazer._busy = False

    @patch('subprocess.Popen')
    def test_program_device_wrong_call(self, Popen):
        Popen.side_effect = Exception("can't create Popen!")

        self.assertRaises(
            jtag_blazer.ErrorProgrammingDeviceError,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

    def test_program_device_wrong_config(self):
        self.jtag_blazer._cfg_manager._values.pop('xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path')
        self.assertRaises(
            jtag_blazer.CantFindJTagBlazerProperty,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )

        self.jtag_blazer._cfg_manager._values.pop('xilinx_jtag_blazer_jbmanager_target_full_path')
        self.assertRaises(
            jtag_blazer.CantFindJTagBlazerProperty,
            self.jtag_blazer.program_device,
            "file.svf", "0.0.0.0"
        )


def suite():
    return unittest.makeSuite(JTagBlazerTestCase)

if __name__ == '__main__':
    unittest.main()
