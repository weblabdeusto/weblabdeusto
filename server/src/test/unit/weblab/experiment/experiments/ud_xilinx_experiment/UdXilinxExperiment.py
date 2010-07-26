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

class FakeJTagBlazer(object):
    def __init__(self):
        super(FakeJTagBlazer,self).__init__()
    def program_device(self, svf_file_name, device_ip):
        pass

class FakeHttpDevice(object):
    def __init__(self):
        super(FakeHttpDevice, self).__init__()
        self.sent = 0
        self.msgs = []
    def send_message(self, msg):
        self.sent += len(msg)
        self.msgs.append(msg)
        

class UdXilinxExperimentTestCase(unittest.TestCase):
    
    def test_xilinx_with_serial_port(self):

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        
        cfg_manager._set_value('xilinx_use_jtag_blazer_to_program', False)
        cfg_manager._set_value('xilinx_use_http_to_send_commands', False)
        
        self.uxm = UdXilinxExperiment.UdXilinxExperiment(
                None,
                None,
                cfg_manager
            )        
        
        # Hook _xilinx_impact and _serial_port
        self.uxm._xilinx_impact = FakeImpact()
        self.uxm._serial_port   = FakeSerialPort()

        # No problem
        self.uxm.do_send_file_to_device(ExperimentUtil.serialize("whatever " * 400), 'program')

        initial_open  = 20
        initial_send  = 20
        initial_close = 20

        self.assertEquals(
                initial_open,
                self.uxm._serial_port.dict['open']
            )
        self.assertEquals(
                initial_close,
                self.uxm._serial_port.dict['close']
            )
        self.assertEquals(
                initial_send,
                self.uxm._serial_port.dict['send']
            )
        self.assertEquals(
                initial_send,
                len(self.uxm._serial_port.codes)
            )


        self.uxm.do_send_command_to_device("ClockActivation off, ClockActivation on 1500, SetPulse on 3")

        self.assertEquals(
                1 + initial_open,
                self.uxm._serial_port.dict['open']
            )
        self.assertEquals(
                1 + initial_close,
                self.uxm._serial_port.dict['close']
            )
        self.assertEquals(
                3 + initial_send,
                self.uxm._serial_port.dict['send']
            )
        self.assertEquals(
                3 + initial_send,
                len(self.uxm._serial_port.codes)
            )
        self.assertEquals(
                37,
                self.uxm._serial_port.codes[0 + initial_send]
            )

        self.assertEquals(
                35,
                self.uxm._serial_port.codes[1 + initial_send]
            )

        self.assertEquals(
                27,
                self.uxm._serial_port.codes[2 + initial_send]
            )

    def test_jtag_blazer_with_http(self):

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        
        cfg_manager._set_value('xilinx_use_jtag_blazer_to_program', True)
        cfg_manager._set_value('xilinx_use_http_to_send_commands', True)
        
        self.uxm = UdXilinxExperiment.UdXilinxExperiment(
                None,
                None,
                cfg_manager
            )        

        # Hook _xilinx_impact and _serial_port
        self.uxm._jtag_blazer = FakeJTagBlazer()
        self.uxm._http_device = FakeHttpDevice()

        # No problem
        self.uxm.do_send_file_to_device(ExperimentUtil.serialize("whatever " * 400), 'program')

        initial_send  = 20

        self.assertEquals(
                initial_send,
                len(self.uxm._http_device.msgs)
            )

        self.uxm.do_send_command_to_device("ClockActivation off, ClockActivation on 1500, SetPulse on 3")

        self.assertEquals(
                1 + initial_send,
                len(self.uxm._http_device.msgs)
            )
        
        self.assertEquals(
                "ClockActivation off, ClockActivation on 1500, SetPulse on 3",
                self.uxm._http_device.msgs[0 + initial_send]
            )
        
def suite():
    return unittest.makeSuite(UdXilinxExperimentTestCase)

if __name__ == '__main__':
    unittest.main()

