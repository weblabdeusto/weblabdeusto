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
import experiments.ud_xilinx.exc as UdXilinxExperimentErrors
from experiments.ud_xilinx import command_senders as UdXilinxCommandSenders
import unittest
import voodoo.configuration as ConfigurationManager

import test.unit.configuration as configuration_module
import weblab.experiment.util as ExperimentUtil
import experiments.ud_xilinx.server as UdXilinxExperiment
import time

class CreatingUdXilinxExperimentTestCase(unittest.TestCase):

    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

    def test_invalid_device_to_program(self):
        self.cfg_manager._set_value('xilinx_device_to_program', 'ThisWillNeverBeAValidDeviceToProgramName')
        self.assertRaises(
            UdXilinxExperimentErrors.InvalidDeviceToProgramError,
            UdXilinxExperiment.UdXilinxExperiment,
            None, None, self.cfg_manager
        )

    def test_invalid_device_to_send_commands(self):
        self.cfg_manager._set_value('xilinx_device_to_send_commands', 'ThisWillNeverBeAValidDeviceToSendCommandsName')
        self.assertRaises(
            UdXilinxExperimentErrors.InvalidDeviceToSendCommandsError,
            UdXilinxExperiment.UdXilinxExperiment,
            None, None, self.cfg_manager
        )

class UsingUdXilinxExperimentTestCase(unittest.TestCase):

    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        UdXilinxCommandSenders._SerialPort = FakeSerialPort
        UdXilinxCommandSenders._HttpDevice = FakeHttpDevice

    def wait_for_programming_to_end(self):
        """
        Helper method which will simply wait until the board programming
        process finishes (the state changes).
        No assumptions are made about its result.
        """
        while(self.uxm.get_state() in (UdXilinxExperiment.STATE_PROGRAMMING, UdXilinxExperiment.STATE_NOT_READY) ):
            time.sleep(0.1)

    def test_xilinx_with_serial_port(self):
        self.cfg_manager._set_value('xilinx_device_to_program', 'XilinxImpact')
        self.cfg_manager._set_value('xilinx_device_to_send_commands', 'SerialPort')

        self.uxm = UdXilinxExperiment.UdXilinxExperiment(
                None,
                None,
                self.cfg_manager
            )

        # No problem
        self.uxm.do_send_file_to_device(ExperimentUtil.serialize("whatever " * 400), 'program')

        self.wait_for_programming_to_end()

        # These were initially 1.
        initial_open  = 1
        initial_send  = 1
        initial_close = 1

        self.assertEquals(
                initial_open,
                self.uxm._command_sender._serial_port.dict['open']
            )
        self.assertEquals(
                initial_close,
                self.uxm._command_sender._serial_port.dict['close']
            )
        self.assertEquals(
                initial_send,
                self.uxm._command_sender._serial_port.dict['send']
            )
        self.assertEquals(
                initial_send,
                len(self.uxm._command_sender._serial_port.codes)
            )

        self.uxm.do_send_command_to_device("ClockActivation off, ClockActivation on 1500, SetPulse on 3")

        self.assertEquals(
                1 + initial_open,
                self.uxm._command_sender._serial_port.dict['open']
            )
        self.assertEquals(
                1 + initial_close,
                self.uxm._command_sender._serial_port.dict['close']
            )
        self.assertEquals(
                3 + initial_send,
                self.uxm._command_sender._serial_port.dict['send']
            )
        self.assertEquals(
                3 + initial_send,
                len(self.uxm._command_sender._serial_port.codes)
            )
        self.assertEquals(
                37,
                self.uxm._command_sender._serial_port.codes[0 + initial_send]
            )

        self.assertEquals(
                35,
                self.uxm._command_sender._serial_port.codes[1 + initial_send]
            )

        self.assertEquals(
                27,
                self.uxm._command_sender._serial_port.codes[2 + initial_send]
            )

    @patch('experiments.ud_xilinx.programmers.JTagBlazer')
    def test_jtag_blazer_with_http(self, _):
        self.cfg_manager._set_value('xilinx_device_to_program', 'JTagBlazer')
        self.cfg_manager._set_value('xilinx_device_to_send_commands', 'HttpDevice')

        self.uxm = UdXilinxExperiment.UdXilinxExperiment(
                None,
                None,
                self.cfg_manager
            )

        # No problem
        self.uxm.do_send_file_to_device(ExperimentUtil.serialize("whatever " * 400), 'program')

        self.wait_for_programming_to_end()

        # Initially 1.
        initial_send  = 1

        #self.assertEquals(
        #        initial_send,
        #        len(self.uxm._command_sender._http_device.msgs)
        #    )

        self.uxm.do_send_command_to_device("ClockActivation off, ClockActivation on 1500, SetPulse on 3")

        # Constant was originally 1.
        self.assertEquals(
                1 + initial_send,
                len(self.uxm._command_sender._http_device.msgs)
            )

        self.assertEquals(
                "ClockActivation off, ClockActivation on 1500, SetPulse on 3",
                self.uxm._command_sender._http_device.msgs[0 + initial_send]
            )

    @patch('subprocess.Popen')
    def test_digilent_adept_with_http(self, Popen):
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.communicate.return_value = ('','')

        self.cfg_manager._set_value('xilinx_device_to_program', 'DigilentAdept')
        self.cfg_manager._set_value('xilinx_device_to_send_commands', 'HttpDevice')

        self.uxm = UdXilinxExperiment.UdXilinxExperiment(
                None,
                None,
                self.cfg_manager
            )

        # No problem
        self.uxm.do_send_file_to_device(ExperimentUtil.serialize("whatever " * 400), 'program')

        self.wait_for_programming_to_end()

        initial_send  = 1

        self.assertEquals(
                initial_send,
                len(self.uxm._command_sender._http_device.msgs)
            )

        self.uxm.do_send_command_to_device("ClockActivation off, ClockActivation on 1500, SetPulse on 3")

        self.assertEquals(
                1 + initial_send,
                len(self.uxm._command_sender._http_device.msgs)
            )

        self.assertEquals(
                "ClockActivation off, ClockActivation on 1500, SetPulse on 3",
                self.uxm._command_sender._http_device.msgs[0 + initial_send]
            )


def suite():
    return unittest.TestSuite(
            (
                # unittest.makeSuite(CreatingUdXilinxExperimentTestCase),
                # unittest.makeSuite(UsingUdXilinxExperimentTestCase)
            )
        )


class FakeImpact(object):
    def __init__(self):
        super(FakeImpact,self).__init__()
    def program_device(self, program_path):
        pass
    def source2svf(self, program_path):
        pass
    def get_suffix(self):
        return "whatever"

class FakeSerialPort(object):
    def __init__(self):
        super(FakeSerialPort,self).__init__()
        self.dict = {'open':0, 'close':0, 'send' : 0}
        self.codes = []
    def _increment(self, sth):
        self.dict[sth] = self.dict[sth] + 1
    def open_serial_port(self, number):
        self._increment('open')
    def send_code(self, n):
        self._increment('send')
        self.codes.append(n)
    def close_serial_port(self):
        self._increment('close')

class FakeHttpDevice(object):
    def __init__(self, *args, **kargs):
        super(FakeHttpDevice, self).__init__()
        self.sent = 0
        self.msgs = []
    def send_message(self, msg):
        self.sent += len(msg)
        self.msgs.append(msg)


if __name__ == '__main__':
    unittest.main()
