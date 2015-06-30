#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import weblab.core.exc as coreExc
from weblab.data.experiments import ExperimentInstanceId
from weblab.core.coordinator.resource import Resource
import weblab.core.coordinator.config_parser as CoordinationConfigurationParser

class CoordinationConfigurationParserTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordination_configuration_parser = CoordinationConfigurationParser.CoordinationConfigurationParser(self.cfg_manager)

    def test_coordination_configuration_parser(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'exp1|ud-fpga|FPGA experiments' : 'fpga1@fpga boards',
                                'exp1|ud-pld|PLD experiments' : 'pld1@pld boards',
                            },
                    })

        configuration = self.coordination_configuration_parser.parse_configuration()
        self.assertEquals(1, len(configuration))
        lab_config = configuration['laboratory1:WL_SERVER1@WL_MACHINE1']
        self.assertEquals(2, len(lab_config))
        exp_fpga = ExperimentInstanceId("exp1","ud-fpga","FPGA experiments")
        exp_pld  = ExperimentInstanceId("exp1","ud-pld","PLD experiments")

        fpga_resource = lab_config[exp_fpga]
        self.assertEquals(Resource("fpga boards", "fpga1"), fpga_resource)

        pld_resource = lab_config[exp_pld]
        self.assertEquals(Resource("pld boards", "pld1"), pld_resource)

    def test_coordination_parse_resources_for_experiment_ids(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'exp1|ud-fpga|FPGA experiments' : 'fpga1@fpga boards',
                                'exp1|ud-pld|PLD experiments'   : 'pld1@pld boards',
                                'exp1|ud-logic|PIC experiments' : 'pld1@pld boards'
                            },
                        'laboratory2:WL_SERVER1@WL_MACHINE1' : {
                                'exp2|ud-fpga|FPGA experiments' : 'fpga1@fpga boards',
                                'exp2|ud-pld|PLD experiments' : 'pld1@pld boards',
                                'exp2|ud-logic|PIC experiments' : 'fpga1@fpga boards'
                            },
                    })
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_EXTERNAL_SERVERS, {
                        'ud-pld@PLD experiments' : ['weblab_university1', 'weblab_university2'],
                        'visir@VISIR experiments' : ['weblab_university3']
                    })

        configuration = self.coordination_configuration_parser.parse_resources_for_experiment_ids()
        self.assertTrue('ud-pld@PLD experiments'   in configuration)
        self.assertTrue('ud-fpga@FPGA experiments' in configuration)
        self.assertTrue('ud-logic@PIC experiments' in configuration)
        self.assertEquals(set(('pld boards','weblab_university1','weblab_university2')),  configuration['ud-pld@PLD experiments'])
        self.assertEquals(set(('weblab_university3',)),  configuration['visir@VISIR experiments'])
        self.assertEquals(set(('fpga boards',)), configuration['ud-fpga@FPGA experiments'])
        self.assertEquals(set(('pld boards', 'fpga boards')), configuration['ud-logic@PIC experiments'])

    def test_coordination_configuration_parser_fail1(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'not.a.valid.experiment.instance.id' : 'fpga1@fpga boards'
                            },
                    })
        self.assertRaises(
            coreExc.CoordinationConfigurationParsingError,
            self.coordination_configuration_parser.parse_configuration
        )

    def test_coordination_configuration_parser_fail2(self):
        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS, {
                        'laboratory1:WL_SERVER1@WL_MACHINE1' : {
                                'exp1|ud-fpga|FPGA experiments' : 'not.a.valid.resource.instance',
                            },
                    })
        self.assertRaises(
            coreExc.CoordinationConfigurationParsingError,
            self.coordination_configuration_parser.parse_configuration
        )




def suite():
    return unittest.makeSuite(CoordinationConfigurationParserTestCase)

if __name__ == '__main__':
    unittest.main()

