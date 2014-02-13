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
# Author: Luis Rodriguez <luis.rodriguezgil@deusto.es>
#

#
# Note: The purpose of creating a new file (test_server_logic.py) rather than using the existing
# test_server.py is mainly because some methods from test_server.py seem to be failing but shouldn't.
# Also, the tests here are meant to be higher level than the test_server.py tests, which seem to be oriented
# towards board-programming, etc.
#
from mock import patch

import json
import mock
import experiments.ud_xilinx.server as UdXilinxExperiment
import experiments.ud_xilinx.exc as UdXilinxExperimentErrors
from experiments.ud_xilinx import command_senders as UdXilinxCommandSenders
import unittest
from test.unit.experiments.ud_xilinx.test_server import FakeSerialPort, FakeHttpDevice
import voodoo.configuration as ConfigurationManager

import test.unit.configuration as configuration_module
import time


# TODO: These tests are very incomplete.
# However, certain "advanced" features are probably required for more effective testing,
# such as the ability to control time.time() returns, etc.

from mock import patch, Mock
import time


# We mock the time so that we can control time.time and time.sleep.

_time = 100

def _sleep_mock_handler(*args, **kwargs):
    global _time
    _time += args[0]

def _time_mock_handler(*args, **kwargs):
    global _time
    return _time


class BasicUdXilinxExperimentTestCase(unittest.TestCase):
    def setUp(self):
        from voodoo.configuration import ConfigurationManager
        from voodoo.sessions.session_id import SessionId

        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value("webcam", "http://localhost")

        # For later.
        self.cfg_manager._set_value("weblab_xilinx_experiment_xilinx_device", "FPGA")

        UdXilinxCommandSenders._SerialPort = FakeSerialPort
        UdXilinxCommandSenders._HttpDevice = FakeHttpDevice

        self.experiment = UdXilinxExperiment.UdXilinxExperiment(None, None, self.cfg_manager)

        self.lab_session_id = SessionId('my-session-id')

    def cleanUp(self):
        pass

    def test_basic_start(self):
        configjson = self.experiment.do_start_experiment()
        self.assertIsNotNone(configjson)

    def test_basic_start_config(self):
        configjson = self.experiment.do_start_experiment()
        self.assertEquals(UdXilinxExperiment.STATE_NOT_READY, self.experiment._current_state)

        initconfig = json.loads(configjson)

        self.assertIsNotNone(initconfig)

        self.assertTrue("initial_configuration" in initconfig)

        config = json.loads(initconfig["initial_configuration"])

        self.assertTrue("webcam" in config)

    def test_basic_start_end(self):
        self.experiment.do_start_experiment()

        self.experiment.do_dispose()


    def test_check_state(self):
        self.experiment.do_start_experiment()
        resp = self.experiment.do_send_command_to_device("STATE")
        self.assertEquals(resp, "STATE=" + UdXilinxExperiment.STATE_NOT_READY)

    # TODO: This test is currently failing. REPORT_SWITCHES shouldn't return a list, but a string.
    def _test_report_switches(self):
        self.experiment.do_start_experiment()
        resp = self.experiment.do_send_command_to_device("REPORT_SWITCHES")
        self.assertEquals("1111111111", resp)

    def test_api_version(self):
        api = self.experiment.do_get_api()
        self.assertEquals("2", api)


class EarlyKickingXilinxExperimentTestCase(unittest.TestCase):
    def setUp(self):
        from voodoo.configuration import ConfigurationManager
        from voodoo.sessions.session_id import SessionId

        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value("webcam", "http://localhost")
        self.cfg_manager._set_value("weblab_xilinx_experiment_xilinx_device", "FPGA")
        self.cfg_manager._set_value("xilinx_max_use_time", "3600")

        UdXilinxCommandSenders._SerialPort = FakeSerialPort
        UdXilinxCommandSenders._HttpDevice = FakeHttpDevice

        self.experiment = UdXilinxExperiment.UdXilinxExperiment(None, None, self.cfg_manager)

        self.lab_session_id = SessionId('my-session-id')


    def test_basic_start_config(self):
        configjson = self.experiment.do_start_experiment()
        self.assertEquals(UdXilinxExperiment.STATE_NOT_READY, self.experiment._current_state)

        initconfig = json.loads(configjson)

        self.assertIsNotNone(initconfig)

        self.assertTrue("initial_configuration" in initconfig)

        config = json.loads(initconfig["initial_configuration"])

        self.assertTrue("webcam" in config)
        self.assertTrue("max_use_time" in config)

    def test_cleanup(self):
        self.experiment.do_start_experiment()
        self.experiment.do_dispose()
        self.assertIsNone(self.experiment._use_time_start)

    def test_report(self):
        self.experiment.do_start_experiment()
        resp = self.experiment.do_send_command_to_device("REPORT_USE_TIME_LEFT")

        self.assertEquals("unknown", resp)


class PermissionsXilinxExperimentTestCase(unittest.TestCase):
    def setUp(self):
        from voodoo.configuration import ConfigurationManager
        from voodoo.sessions.session_id import SessionId

        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value("webcam", "http://localhost")
        self.cfg_manager._set_value("weblab_xilinx_experiment_xilinx_device", "FPGA")
        self.cfg_manager._set_value("xilinx_max_use_time", "3600")
        self.cfg_manager._set_value("xilinx_bit_allowed", False)

        UdXilinxCommandSenders._SerialPort = FakeSerialPort
        UdXilinxCommandSenders._HttpDevice = FakeHttpDevice

        self.experiment = UdXilinxExperiment.UdXilinxExperiment(None, None, self.cfg_manager)
        self.lab_session_id = SessionId('my-session-id')

    def cleanUp(self):
        self.experiment.do_dispose()

    def test_bit_disallowed(self):
        new_state = self.experiment.do_send_file_to_device("CONTENTS", "bit")
        self.assertEquals("STATE=not_allowed", new_state)

    def test_vhd_allowed(self):
        new_state = self.experiment.do_send_file_to_device("CONTENTS", "vhd")
        self.assertNotEquals("STATE=not_allowed", new_state)

    def test_all_disallowed(self):
        new_state = self.experiment.do_send_file_to_device("CONTENTS", "wha");
        self.assertEquals("STATE=not_allowed", new_state)


class CompilerXilinxExperimentTestCase(unittest.TestCase):

    def setUp(self):
        from voodoo.configuration import ConfigurationManager
        from voodoo.sessions.session_id import SessionId

        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value("webcam", "http://localhost")

        # For later.
        self.cfg_manager._set_value("weblab_xilinx_experiment_xilinx_device", "FPGA")

        UdXilinxCommandSenders._SerialPort = FakeSerialPort
        UdXilinxCommandSenders._HttpDevice = FakeHttpDevice

        self.experiment = UdXilinxExperiment.UdXilinxExperiment(None, None, self.cfg_manager)

        self.configjson = self.experiment.do_start_experiment()

        self.lab_session_id = SessionId('my-session-id')

    @mock.patch("experiments.xilinxc.compiler.Compiler")
    def test_compile(self, compiler_class):
        pass
        # TODO: Test isn't working for now.
        # thr = self.experiment._compile_program_file_t("CONTENTS")
        # print thr

    def cleanUp(self):
        self.experiment.do_dispose()


class VirtualWorldXilinxExperimentTestCase(unittest.TestCase):
    def setUp(self):
        from voodoo.configuration import ConfigurationManager
        from voodoo.sessions.session_id import SessionId

        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value("webcam", "http://localhost")

        # For later.
        self.cfg_manager._set_value("weblab_xilinx_experiment_xilinx_device", "FPGA")

        UdXilinxCommandSenders._SerialPort = FakeSerialPort
        UdXilinxCommandSenders._HttpDevice = FakeHttpDevice

        self.experiment = UdXilinxExperiment.UdXilinxExperiment(None, None, self.cfg_manager)

        self.configjson = self.experiment.do_start_experiment()

        self.lab_session_id = SessionId('my-session-id')

    def cleanUp(self):
        self.experiment.do_dispose()

    def test_basic_state_command(self):
        resp = self.experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
        self.assertEquals("{}", resp)

    def _test_virtualworld_mode_command(self):
        resp = self.experiment.do_send_command_to_device("VIRTUALWORLD_MODE watertank")
        self.assertEquals("ok", resp)

    def test_virtualworld_non_existant(self):
        resp = self.experiment.do_send_command_to_device("VIRTUALWORLD_MODE thisdoesntexist")
        self.assertEquals("unknown_virtualworld", resp)




    class FakeOpen(object):
        def read(self):
            return """
                {
                    "inputs" : [
                        {
                            "inputNumber": "0",
                            "value": "0"
                        },
                        {
                            "inputNumber": "1",
                            "value": "1"
                        },
                        {
                            "inputNumber": "2",
                            "value": "1"
                        },
                        {
                            "inputNumber": "3",
                            "value": "0"
                        },
                        {
                            "inputNumber": "4",
                            "value": "1"
                        },
                        {
                            "inputNumber": "5",
                            "value": "1"
                        },
                        {
                            "inputNumber": "6",
                            "value": "0"
                        },
                        {
                            "inputNumber": "7",
                            "value": "1"
                        }
                    ]
                }
            """

    def _ret_fake(self):
        return VirtualWorldXilinxExperimentTestCase.FakeOpen()

    @patch("urllib2.urlopen", new=_ret_fake)
    def test_read_leds(self):
        resp = self.experiment.query_leds_from_json()
        self.assertEquals(["0", "1", "1", "0", "1", "1", "0", "1"], resp)

        resp = self.experiment.do_send_command_to_device("READ_LEDS")
        self.assertEquals("01101101", resp)


def suite():
    return unittest.TestSuite(
        (
            unittest.makeSuite(BasicUdXilinxExperimentTestCase),
            unittest.makeSuite(PermissionsXilinxExperimentTestCase),
            unittest.makeSuite(EarlyKickingXilinxExperimentTestCase),
            unittest.makeSuite(VirtualWorldXilinxExperimentTestCase)
        )
    )


class FakeImpact(object):
    def __init__(self):
        super(FakeImpact, self).__init__()

    def program_device(self, program_path):
        pass

    def source2svf(self, program_path):
        pass

    def get_suffix(self):
        return "whatever"


class FakeSerialPort(object):
    def __init__(self):
        super(FakeSerialPort, self).__init__()
        self.dict = {'open': 0, 'close': 0, 'send': 0}
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
