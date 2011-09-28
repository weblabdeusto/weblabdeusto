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

import voodoo.gen.loader.ServerLoader as ServerLoader

FEDERATED_DEPLOYMENTS = 'test/deployments/federated_basic'

CONSUMER_CONFIG_PATH  = FEDERATED_DEPLOYMENTS + '/consumer/'
PROVIDER1_CONFIG_PATH = FEDERATED_DEPLOYMENTS + '/provider1/'
PROVIDER2_CONFIG_PATH = FEDERATED_DEPLOYMENTS + '/provider2/'

class FederatedWebLabDeustoTestCase(unittest.TestCase):
    def setUp(self):
        self.server_loader     = ServerLoader.ServerLoader()

        self.consumer_handler  = self.server_loader.load_instance( CONSUMER_CONFIG_PATH,   'main_machine', 'main_instance' )
        self.provider1_handler = self.server_loader.load_instance( PROVIDER1_CONFIG_PATH,  'main_machine', 'main_instance' )
        self.provider2_handler = self.server_loader.load_instance( PROVIDER2_CONFIG_PATH,  'main_machine', 'main_instance' )

    def tearDown(self):
        self.consumer_handler.stop()
        self.provider1_handler.stop()
        self.provider2_handler.stop()

    def test_local_experiment(self):
        pass

    def test_remote_experiment(self):
        pass


def suite():
    suites = (unittest.makeSuite(FederatedWebLabDeustoTestCase), )
    return unittest.TestSuite( suites )

if __name__ == '__main__':
    unittest.main()


