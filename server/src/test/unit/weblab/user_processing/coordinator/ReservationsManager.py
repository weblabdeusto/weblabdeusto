#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

from weblab.data.experiments.ExperimentId import ExperimentId
from weblab.data.experiments.ExperimentInstanceId import ExperimentInstanceId
from weblab.user_processing.coordinator.Resource import Resource
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc

from test.unit.weblab.user_processing.coordinator.Coordinator import WrappedCoordinator, ConfirmerMock

class ReservationsManagerTestCase(unittest.TestCase):
    def setUp(self):

        locator_mock = None

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = WrappedCoordinator(locator_mock, self.cfg_manager, ConfirmerClass = ConfirmerMock)
        self.coordinator._clean()

        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('inst1', 'exp1','cat1'), Resource("res_type", "res_inst1"))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('inst2', 'exp2','cat1'), Resource("res_type", "res_inst2"))

        self.reservations_manager = self.coordinator.reservations_manager

    def test_list_sessions_not_existing(self):
        exp_id = ExperimentId("exp.that.doesnt.exist","cat1")
        
        self.assertRaises(
            CoordExc.ExperimentNotFoundException,
            self.reservations_manager.list_sessions,
            exp_id
        )

    def test_list_sessions(self):
        exp_id1 = ExperimentId("exp1","cat1")
        exp_id2 = ExperimentId("exp2","cat1")

        sessions = self.reservations_manager.list_sessions(exp_id1)
        self.assertEquals(0, len(sessions))

        reservation1 = self.reservations_manager.create(exp_id1, "{}")
        reservation2 = self.reservations_manager.create(exp_id1, "{}")

        self.reservations_manager.create(exp_id2, "{}")
        
        sessions = self.reservations_manager.list_sessions(exp_id1)
        self.assertEquals(2, len(sessions))
        self.assertTrue(reservation1 in sessions)
        self.assertTrue(reservation2 in sessions)

def suite():
    return unittest.makeSuite(ReservationsManagerTestCase)

if __name__ == '__main__':
    unittest.main()

