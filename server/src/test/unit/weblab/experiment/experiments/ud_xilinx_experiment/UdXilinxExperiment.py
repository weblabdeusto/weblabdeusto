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

import weblab.experiment.experiments.ud_xilinx_experiment.UdXilinxExperiment as UdXilinxExperiment
import weblab.experiment.Util as ExperimentUtil
import voodoo.configuration.ConfigurationManager as ConfigurationManager

class FakeImpact(object):
    def __init__(self):
        super(FakeImpact,self).__init__()
    def program_device(self, program_path):
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

class UdXilinxExperimentTestCase(unittest.TestCase):
    def test_general(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        uxm = UdXilinxExperiment.UdXilinxExperiment(
                None,
                None,
                cfg_manager
            )

        # Hook _xilinx_impact and _serial_port
        uxm._xilinx_impact = FakeImpact()
        uxm._serial_port   = FakeSerialPort()

        self.assertEquals(
                0,
                uxm._serial_port.dict['open']
            )
        self.assertEquals(
                0,
                uxm._serial_port.dict['close']
            )
        self.assertEquals(
                0,
                uxm._serial_port.dict['send']
            )
        self.assertEquals(
                0,
                len(uxm._serial_port.codes)
            )

        # No problem
        uxm.do_send_file_to_device(ExperimentUtil.serialize(open(__file__).read()), 'program')

        initial_open  = 1
        initial_send  = 20
        initial_close = 1

        self.assertEquals(
                initial_open,
                uxm._serial_port.dict['open']
            )
        self.assertEquals(
                initial_close,
                uxm._serial_port.dict['close']
            )
        self.assertEquals(
                initial_send,
                uxm._serial_port.dict['send']
            )
        self.assertEquals(
                initial_send,
                len(uxm._serial_port.codes)
            )


        uxm.do_send_command_to_device("ClockActivation off, ClockActivation on 1500, SetPulse on 3")

        self.assertEquals(
                1 + initial_open,
                uxm._serial_port.dict['open']
            )
        self.assertEquals(
                1 + initial_close,
                uxm._serial_port.dict['close']
            )
        self.assertEquals(
                3 + initial_send,
                uxm._serial_port.dict['send']
            )
        self.assertEquals(
                3 + initial_send,
                len(uxm._serial_port.codes)
            )
        self.assertEquals(
                37,
                uxm._serial_port.codes[0 + initial_send]
            )

        self.assertEquals(
                35,
                uxm._serial_port.codes[1 + initial_send]
            )

        self.assertEquals(
                27,
                uxm._serial_port.codes[2 + initial_send]
            )

def suite():
    return unittest.makeSuite(UdXilinxExperimentTestCase)

if __name__ == '__main__':
    unittest.main()

