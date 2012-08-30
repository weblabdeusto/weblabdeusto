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

import voodoo.gen.protocols.XMLRPC.ClientXMLRPC as ClientXMLRPC
import voodoo.gen.protocols.XMLRPC.Errors as Exceptions
import voodoo.gen.exceptions.protocols.ProtocolErrors as ProtocolErrors

import xmlrpclib

class ClientXMLRPCTestCase(unittest.TestCase):
    def test_method(self):
        msg1 = 'Hello '
        msg2 = 'world'
        methods = ('method1','method2','method3')


        class Fake(object):
            def __init__(self):
                self._server = self

            def method1(self, arg1):
                return arg1 + msg2
            def method2(self):
                raise xmlrpclib.Fault("myklazz","it doesn't really matter")
            def method3(self):
                raise NameError('ha ha')

        setattr(Fake, 'Util.method1', Fake.method1)
        setattr(Fake, 'Util.method2', Fake.method2)
        setattr(Fake, 'Util.method3', Fake.method3)

        fake = Fake()

        newfunctions = []
        for i in methods:
            newfunction = ClientXMLRPC._generate_stub(i)
            newfunctions.append(newfunction)

        self.assertEquals(msg1 + msg2,newfunctions[0](fake,msg1))

        self.assertRaises(
                Exceptions.UnknownFaultType,
                newfunctions[1],
                fake
            )

        self.assertRaises(
                ProtocolErrors.UnknownRemoteError,
                newfunctions[2],
                fake
            )

    def test_generation(self):
        ClientXMLRPC.generate(['method1'])
        #No news are good news :-D



def suite():
    return unittest.makeSuite(ClientXMLRPCTestCase)

if __name__ == '__main__':
    unittest.main()

