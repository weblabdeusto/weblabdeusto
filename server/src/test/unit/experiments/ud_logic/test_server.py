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
#
from __future__ import print_function, unicode_literals
import unittest
import test.unit.configuration as configuration_module

import voodoo.configuration as ConfigurationManager
import experiments.logic.server as LogicExperiment

class CircuitGeneratorTestCase(unittest.TestCase):
    def test_switch(self):
        switch = LogicExperiment.Switch()
        self.assertFalse(switch.turned)
        switch.set_turned(True)
        self.assertTrue(switch.turned)

    def test_gate(self):

        switch1 = LogicExperiment.Switch()
        switch2 = LogicExperiment.Switch()
        switch3 = LogicExperiment.Switch()
        switch4 = LogicExperiment.Switch()

        gate2 = LogicExperiment.Gate('and', switch1, switch2)
        gate3 = LogicExperiment.Gate('and', switch3, switch4)
        gate1 = LogicExperiment.Gate('or', gate2, gate3)

        self.assertFalse(gate1.turned)
        switch1.set_turned(True)
        self.assertFalse(gate1.turned)
        switch2.set_turned(True)
        self.assertTrue(gate1.turned)
        switch2.set_turned(False)
        self.assertFalse(gate1.turned)
        switch3.set_turned(True)
        self.assertFalse(gate1.turned)
        switch4.set_turned(True)
        self.assertTrue(gate1.turned)

    def test_generator(self):
        cg = LogicExperiment.CircuitGenerator()
        for _ in xrange(50):
            circuit = cg.generate()
            self.assertTrue(circuit.is_correct_sample())

class WrappedLogicExperiment(LogicExperiment.LogicExperiment):
    def turn_off(self, *args):
        pass
    def send(self, *args):
        pass

class LogicExperimentTestCase(unittest.TestCase):
    def setUp(self):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        self.experiment = WrappedLogicExperiment(None, None, cfg_manager)
        self.experiment.do_start_experiment("{}","{}")

    def test_get_circuit(self):
        circuit1a = self.experiment.do_send_command_to_device('GET_CIRCUIT')
        circuit1b = self.experiment.do_send_command_to_device('GET_CIRCUIT')
        self.assertEquals(circuit1a, circuit1b)

        any_ok = False
        for _ in xrange(10):
            for operation in LogicExperiment.Gate.operations:
                result = self.experiment.do_send_command_to_device('SOLVE %s' % operation)
                if result.startswith('OK'):
                    self.assertEquals(result, 'OK: 1')
                    any_ok = True
                    break
            if any_ok:
                break

        self.assertTrue(any_ok)
        circuit2 = self.experiment.do_send_command_to_device('GET_CIRCUIT')
        self.assertNotEquals(circuit1a, circuit2)

    def test_invalid_command(self):
        response = self.experiment.do_send_command_to_device('foo')
        self.assertTrue(response.startswith('Error'))

    def test_invalid_operation(self):
        response = self.experiment.do_send_command_to_device('SOLVE foo')
        self.assertTrue(response.startswith('Error'))

def suite():
    return unittest.TestSuite((
                unittest.makeSuite(CircuitGeneratorTestCase),
                unittest.makeSuite(LogicExperimentTestCase)
            ))

if __name__ == '__main__':
    unittest.main()


