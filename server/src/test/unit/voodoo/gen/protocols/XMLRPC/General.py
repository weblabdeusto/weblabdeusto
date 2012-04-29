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
import unittest

from test.util.module_disposer import uses_module

import voodoo.gen.protocols.XMLRPC.server as ServerXMLRPC
import voodoo.gen.protocols.XMLRPC.errors as Exceptions

import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.generators as gens

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

PORT = 12047

class GeneralXMLRPCTestCase(unittest.TestCase):

    @uses_module(ServerXMLRPC)
    def test_exceptions(self):
        methods = ["method1","method2"]
        msg1 = "hello"
        msg2 = " world"
        exc_msg = "Haw haw! (with Nelson's voice)"

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        class Ser(gens.ServerSkel.factory(cfg_manager,Protocols.XMLRPC,methods)):
            def do_method1(self,arg):
                return arg + msg2
            def do_method2(self):
                raise ArithmeticError(exc_msg)

        server = Ser(XMLRPC = ('',PORT))
        server.start()

        # Avoid debug info
        client = gens.ClientSkel.factory(Protocols.XMLRPC,methods)(
                    'localhost',
                    PORT
                )

        self.assertEquals(client.method1(msg1),msg1 + msg2)

        self.assertRaises(
                Exceptions.UnknownFaultType,
                client.method2
            )

def suite():
    return unittest.makeSuite(GeneralXMLRPCTestCase)

if __name__ == '__main__':
    unittest.main()

