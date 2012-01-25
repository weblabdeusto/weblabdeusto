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

import voodoo.gen.coordinator.AccessLevel  as AccessLevel
import voodoo.gen.loader.ConfigurationParser as ConfigurationParser
import voodoo.gen.loader.CoordinatorMapBuilder as CoordinatorMapBuilder

import voodoo.gen.protocols.protocols as Protocols

import test.unit.voodoo.gen.loader.ServerType as ServerType

GLOBAL_PATH    = 'test/deployments/WebLabSkel/'

class CoordinatorMapBuilderTestCase(unittest.TestCase):
    def setUp(self):
        global_parser = ConfigurationParser.GlobalParser()
        self.global_configuration = global_parser.parse(GLOBAL_PATH)

    def test_map_loaded(self):
        coordinatorMapBuilder = CoordinatorMapBuilder.CoordinatorMapBuilder()
        map = coordinatorMapBuilder.build(self.global_configuration)

        map['NAME_OF_MACHINE1']
        map['NAME_OF_MACHINE1']['NAME_OF_INSTANCE1']
        server1   = map['NAME_OF_MACHINE1']['NAME_OF_INSTANCE1']['NAME_OF_SERVER1']
        map['NAME_OF_MACHINE1']['NAME_OF_INSTANCE1']['NAME_OF_SERVER2']
        map['NAME_OF_MACHINE1']['NAME_OF_INSTANCE2']

        self.assertEquals(
                ServerType.Login,
                server1.server_type
            )

        self.assertEquals(
                2,
                len([i for i in server1.get_accesses()])
            )

        accesses1 = server1.get_accesses()
        access1   = accesses1.next()
        access2   = accesses1.next()

        self.assertEquals(
                Protocols.Direct,
                access1.protocol
            )
        self.assertEquals(
                AccessLevel.instance,
                access1.access_level
            )
        self.assertEquals(
                1,
                len(access1.networks)
            )

        self.assertEquals(
                Protocols.XMLRPC,
                access2.protocol
            )
        self.assertEquals(
                AccessLevel.network,
                access2.access_level
            )
        self.assertEquals(
                2,
                len(access2.networks)
            )

def suite():
    return unittest.makeSuite(CoordinatorMapBuilderTestCase)

if __name__ == '__main__':
    unittest.main()


