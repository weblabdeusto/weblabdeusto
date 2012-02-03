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

import voodoo.gen.loader.ServerLoader as ServerLoader

GLOBAL_CONFIGURATION_PATH = 'test/deployments/WebLabSkel'

class ServerLoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.server_loader = ServerLoader.ServerLoader()

    def test_load_instance(self):
        instance_handler = self.server_loader.load_instance(
                GLOBAL_CONFIGURATION_PATH,
                'NAME_OF_MACHINE1',
                'NAME_OF_INSTANCE1'
            )
        instance_handler.stop()


def suite():
    return unittest.TestSuite(
        (
            unittest.makeSuite(ServerLoaderTestCase),
        )
    )

if __name__ == '__main__':
    unittest.main()

