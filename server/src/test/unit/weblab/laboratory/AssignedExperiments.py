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

import weblab.exceptions.laboratory.LaboratoryExceptions as LaboratoryExceptions

import weblab.laboratory.AssignedExperiments as AssignedExperiments
import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId

class AssignedExperimentsTestCase(unittest.TestCase):
    def setUp(self):
        self._assigned_micro_servers = AssignedExperiments.AssignedExperiments()
        self.exp_inst_id = ExperimentInstanceId.ExperimentInstanceId("exp_inst","exp_name","exp_cat")
        
    
    def test_add_server(self):
        clients_coord_addresses = CoordAddress.CoordAddress.translate_address("myserver:myinstance@mymachine")

        self._assigned_micro_servers.add_server( self.exp_inst_id, clients_coord_addresses )

        self.assertRaises(
            LaboratoryExceptions.ExperimentAlreadyFoundException,
            self._assigned_micro_servers.add_server,
            self.exp_inst_id,
            clients_coord_addresses
        )

    def test_get_coord_address(self):
        clients_coord_addresses = CoordAddress.CoordAddress.translate_address("myserver:myinstance@mymachine")

        self._assigned_micro_servers.add_server( self.exp_inst_id, clients_coord_addresses )

        coord_address = self._assigned_micro_servers.get_coord_address(self.exp_inst_id)
        self.assertEquals(clients_coord_addresses, coord_address)

    def test_get_lab_session_id(self):
        clients_coord_addresses = CoordAddress.CoordAddress.translate_address("myserver:myinstance@mymachine")

        self._assigned_micro_servers.add_server( self.exp_inst_id, clients_coord_addresses )

        self._assigned_micro_servers.reserve_experiment(self.exp_inst_id, "foo")
        lab_session_id = self._assigned_micro_servers.get_lab_session_id(self.exp_inst_id)
        self.assertEquals("foo", lab_session_id)


    def test_reserve_experiment(self):
        clients_coord_addresses = CoordAddress.CoordAddress.translate_address("myserver:myinstance@mymachine")

        self._assigned_micro_servers.add_server( self.exp_inst_id, clients_coord_addresses )

        def check_reserve():
            result = self._assigned_micro_servers.reserve_experiment( self.exp_inst_id, "my session id" )

            self.assertEquals( clients_coord_addresses, result )

            self.assertRaises(
                LaboratoryExceptions.BusyExperimentException,
                self._assigned_micro_servers.reserve_experiment,
                self.exp_inst_id,
                "my session id"
            )
        check_reserve()
        self._assigned_micro_servers.free_experiment(self.exp_inst_id)
        check_reserve()
        self._assigned_micro_servers.free_experiment(self.exp_inst_id)
        self.assertRaises(
            LaboratoryExceptions.AlreadyFreedExperimentException,
            self._assigned_micro_servers.free_experiment,
            self.exp_inst_id 
        )

    def test_bounds(self):
        self.assertRaises(
            LaboratoryExceptions.ExperimentNotFoundException,
            self._assigned_micro_servers.reserve_experiment,
            self.exp_inst_id,
            "my session id"
        )

def suite():
    return unittest.makeSuite(AssignedExperimentsTestCase)

if __name__ == '__main__':
    unittest.main()

