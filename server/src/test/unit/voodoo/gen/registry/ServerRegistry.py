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

import voodoo.gen.registry.server_registry as ServerRegistry
import voodoo.gen.exceptions.registry.RegistryExceptions as RegistryExceptions



class ServerRegistryTestCase(unittest.TestCase):
    def test_registries(self):
        reg1 = ServerRegistry.get_instance()
        reg2 = ServerRegistry.get_instance()
        self.assertEquals(
                reg1,
                reg2
            )
    def tearDown(self):
        ServerRegistry.get_instance().clear()

    def test_server(self):
        self._registry = ServerRegistry.get_instance()
        address1 = 'address1'
        address2 = 'address2'
        address3 = 'address3'

        server1 = 'server1'
        server2 = 'server2'

        self._registry.register_server(address1,server1)

        self.assertRaises(
            RegistryExceptions.AddressAlreadyRegisteredException,
            self._registry.register_server,
            address1,
            server2
        )

        self._registry.reregister_server(address1,server2)
        self._registry.reregister_server(address2,server2)
        self._registry.reregister_server(address2,server2)

        self.assertEquals(
            self._registry.get_server(address1),
            server2
        )
        self.assertEquals(
            self._registry.get_server(address2),
            server2
        )

        self.assertRaises(
            RegistryExceptions.ServerNotFoundInRegistryException,
            self._registry.get_server,
            address3
        )

        self._registry.deregister_server(address1)
        self.assertRaises(
            RegistryExceptions.ServerNotFoundInRegistryException,
            self._registry.get_server,
            address1
        )

        self.assertRaises(
            RegistryExceptions.ServerNotFoundInRegistryException,
            self._registry.deregister_server,
            address3
        )

        self._registry.clear()
        self.assertRaises(
            RegistryExceptions.ServerNotFoundInRegistryException,
            self._registry.deregister_server,
            address2
        )

def suite():
    return unittest.makeSuite(ServerRegistryTestCase)

if __name__ == '__main__':
    unittest.main()

