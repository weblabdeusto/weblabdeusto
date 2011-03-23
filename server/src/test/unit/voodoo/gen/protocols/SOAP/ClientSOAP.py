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

from test.util.optional_modules import OptionalModuleTestCase
import voodoo.gen.protocols.SOAP.ClientSOAP as ClientSOAP
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP
import voodoo.gen.protocols.SOAP.Exceptions as Exceptions
import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

try:
    import SOAPpy
except ImportError:
    pass

class ClientSOAPTestCase(unittest.TestCase):
    if ClientSOAP.SOAPPY_AVAILABLE:
        def test_method(self):
            msg1 = 'Hello '
            msg2 = 'world'
            exc_msg = "Haw haw! -with Nelson's voice"
            methods = ('method1','method2','method3','method4')

            class Fake:
                def __init__(self):
                    self._server = self
                def method1(self, arg1):
                    return arg1 + msg2
                def method2(self):
                    raise SOAPpy.faultType(
                            faultcode='exceptions.TypeError',
                            faultstring=exc_msg,
                            detail = "it doesn't really matter"
                        )
                def method3(self):
                    raise SOAPpy.faultType(
                            faultcode='this.class.does.not.exist',
                            faultstring="this won't be read",
                            detail = "it doesn't really matter"
                        )

                def method4(self):
                    raise NameError('ha ha')
            
            fake = Fake()
            
            newfunctions = []
            for i in methods:
                newfunction = ClientSOAP._generate_stub(i)
                newfunctions.append(newfunction)
        
            if ServerSOAP.SERIALIZE:
                #TODO: this must be tested
                return
            self.assertEquals(msg1 + msg2,newfunctions[0](fake,msg1))
            
            self.assertRaises(
                    TypeError,
                    newfunctions[1],
                    fake
                )
            
            the_error = None
            try:
                newfunctions[1](fake)
            except TypeError,te:
                the_error = te
                
            self.assertEquals( the_error.args[0], exc_msg )

            self.assertRaises(
                    Exceptions.UnknownFaultType,
                    newfunctions[2],
                    fake
                )

            self.assertRaises(
                    ProtocolExceptions.UnknownRemoteException,
                    newfunctions[3],
                    fake
                )

        def test_generation(self):
            ClientSOAP.generate(['method1'])
            #No news are good news :-D
    else:
        print >> sys.stderr, "Skipping tests at ClientSOAPTestCase because SOAPpy is not installed"

class SOAPpyNotAvailableTestCase(OptionalModuleTestCase):
    MODULE    = ClientSOAP
    ATTR_NAME = 'SOAPPY_AVAILABLE'

    def test_soappy_not_available(self):
        def func():
            ClientClass = ClientSOAP.generate(['method1'])
            ClientClass('', 10464)

        self._test_func_without_module(func)


def suite():
    return unittest.TestSuite((
                        unittest.makeSuite(ClientSOAPTestCase),
                        unittest.makeSuite(SOAPpyNotAvailableTestCase)
                    ))

if __name__ == '__main__':
    unittest.main()

