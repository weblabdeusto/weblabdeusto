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

import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
from weblab.user_processing.coordinator.Resource import Resource
import weblab.user_processing.coordinator.CoordinationConfigurationParser as CoordinationConfigurationParser

class CoordinationConfigurationParserTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordination_configuration_parser = CoordinationConfigurationParser.CoordinationConfigurationParser(self.cfg_manager)

    def test_coordination_configuration_parser(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'exp1|ud-fpga|FPGA experiments' : 'fpga1@ud-fpga-board',
                                'exp1|ud-pld|PLD experiments' : 'pld1@ud-pld-board',
                            },
                    })

        configuration = self.coordination_configuration_parser.parse_configuration()
        self.assertEquals(1, len(configuration))
        lab_config = configuration['laboratory1:WL_SERVER1@WL_MACHINE1']
        self.assertEquals(2, len(lab_config))
        exp_fpga = ExperimentInstanceId.ExperimentInstanceId("exp1","ud-fpga","FPGA experiments")
        exp_pld  = ExperimentInstanceId.ExperimentInstanceId("exp1","ud-pld","PLD experiments")

        fpga_resource = lab_config[exp_fpga]
        self.assertEquals(Resource("ud-fpga-board", "fpga1"), fpga_resource)

        pld_resource = lab_config[exp_pld]
        self.assertEquals(Resource("ud-pld-board", "pld1"), pld_resource)

    def test_coordination_configuration_parser_fail1(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'not.a.valid.experiment.instance.id' : 'fpga1@ud-fpga-board'
                            },
                    })
        self.assertRaises(
            UserProcessingExceptions.CoordinationConfigurationParsingException,
            self.coordination_configuration_parser.parse_configuration
        )
       
    def test_coordination_configuration_parser_fail2(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'exp1|ud-fpga|FPGA experiments' : 'not.a.valid.resource.instance',
                            },
                    })
        self.assertRaises(
            UserProcessingExceptions.CoordinationConfigurationParsingException,
            self.coordination_configuration_parser.parse_configuration
        )
       



def suite():
    return unittest.makeSuite(CoordinationConfigurationParserTestCase)

if __name__ == '__main__':
    unittest.main()

