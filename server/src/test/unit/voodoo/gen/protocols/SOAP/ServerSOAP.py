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
from test.util.optional_modules import OptionalModuleTestCase
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP

try:
    import SOAPpy
except ImportError:
    pass

PORT = 12345

class ServerSOAPTestCase(unittest.TestCase):
    if ServerSOAP.SOAPPY_AVAILABLE:
        @uses_module(ServerSOAP)
        def test_method(self):
            msg1 = "hello"
            msg2 = " world"
            exc_msg = "Haw haw! (with Nelson's voice)"
            methods = ('method1','method2')
            class Fake:
                def __init__(self):
                    self._parent = self
                def do_method1(self,arg1):
                    return arg1 + msg2
                def do_method2(self,arg1):
                    raise ArithmeticError(exc_msg)
            fake = Fake()

            newfunctions = []
            for i in methods:
                newfunction = ServerSOAP._generate_skeleton(i)
                newfunctions.append(newfunction)

            if ServerSOAP.SERIALIZE:
                #TODO: this must be tested
                return
            self.assertEquals(msg1 + msg2,newfunctions[0](fake,msg1))
            self.assertRaises(
                    SOAPpy.faultType,
                    newfunctions[1],
                    fake,
                    msg1
                )
            the_fault = None
            try:
                newfunctions[1](fake,msg1)
            except SOAPpy.faultType, ft:
                the_fault = ft

            self.assertEquals( the_fault.faultstring, exc_msg )
            self.assertEquals( the_fault.faultcode, 'exceptions.ArithmeticError' )

    else:
        print >> sys.stderr, "ServerSOAPTestCase skipped; SOAPpy not available"

class SOAPpyNotAvailableTestCase(OptionalModuleTestCase):
    MODULE    = ServerSOAP
    ATTR_NAME = 'SOAPPY_AVAILABLE'

    @uses_module(ServerSOAP)
    def test_soappy_not_available(self):
        def func():
            ServerClass = ServerSOAP.generate(None, ['method1','method2'])
            server_instance = ServerClass('', 10464)

        self._test_func_without_module(func)

def suite():
    return unittest.TestSuite((
                    unittest.makeSuite(ServerSOAPTestCase),
                    unittest.makeSuite(SOAPpyNotAvailableTestCase)
                ))

if __name__ == '__main__':
    unittest.main()

