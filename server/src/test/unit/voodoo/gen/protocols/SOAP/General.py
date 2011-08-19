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
import sys
import unittest

from test.util.ModuleDisposer import uses_module
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP

import voodoo.gen.protocols.Protocols as Protocols
import voodoo.gen.generators as gens

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

PORT = 12346

class GeneralSOAPTestCase(unittest.TestCase):
    if ServerSOAP.SOAPPY_AVAILABLE:
        @uses_module(ServerSOAP)
        def test_exceptions(self):
            methods = ["method1","method2"]
            msg1 = "hello"
            msg2 = " world"
            exc_msg = "Haw haw! (with Nelson's voice)"

            cfg_manager= ConfigurationManager.ConfigurationManager()
            cfg_manager.append_module(configuration_module)

            class Ser(gens.ServerSkel.factory(cfg_manager,Protocols.SOAP,methods)):
                def do_method1(self,arg):
                    return arg + msg2
                def do_method2(self):
                    raise ArithmeticError(exc_msg)

            server = Ser(SOAP = ('',PORT))
            server.start()

            # Avoid debug info
            server._servers['SOAP'].server.config.dumpFaultInfo = 0

            client = gens.ClientSkel.factory(Protocols.SOAP,methods)(
                        'localhost',
                        PORT
                    )
            
            self.assertEquals(client.method1(msg1),msg1 + msg2)

            self.assertRaises(
                    ArithmeticError,
                    client.method2
                )
            
            my_error = None
            try:
                client.method2()
            except ArithmeticError as ae:
                my_error = ae

            self.assertEquals(
                    my_error.args[0],
                    exc_msg
                )
    else:
        print >> sys.stderr, "GeneralSOAPTestCase skipped; SOAPpy not installed"
        

def suite():
    return unittest.makeSuite(GeneralSOAPTestCase)

if __name__ == '__main__':
    unittest.main()

