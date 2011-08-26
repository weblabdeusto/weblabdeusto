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

from test.util.module_disposer import uses_module

import voodoo.gen.protocols.SOAP.Address as SOAPAddress
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP

import voodoo.gen.generators.ServerSkel as ServerSkel
import voodoo.gen.protocols.protocols as Protocols

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

class FakeClientClass(object):
    def __init__(self, *args):
        raise Exception("bar")

class FakeClientSOAPModule(object):
    fail = True

    @staticmethod
    def generate(methods):
        if FakeClientSOAPModule.fail:
            raise Exception("foo")
        else:
            return FakeClientClass

class SOAPAddressTestCase(unittest.TestCase):
    def setUp(self):
        self.methods = ['say_hello']
        self.message1 = "hello"
        self.message2 = "olleh"
        self.host = 'localhost'
        self.port = 10005

    if ServerSOAP.SOAPPY_AVAILABLE:
        def test_equals(self):
            soap_addr = SOAPAddress.Address(
                    self.host + ':' + str(self.port) + '@NetworkA'
                )
            soap_addr2 = SOAPAddress.Address(
                    self.host + ':' + str(self.port) + '@NetworkA'
                )
            soap_addr3 = SOAPAddress.Address(
                    self.host + ':' + str(self.port) + '@NetworkB'
                )
            soap_addr4 = SOAPAddress.Address(
                    self.host + ':' + str(self.port+1) + '@NetworkA'
                )
            soap_addr5 = SOAPAddress.Address(
                    self.host +'.' + ':' + str(self.port) + '@NetworkA'
                )
            self.assertEquals(soap_addr,soap_addr2)
            self.assertNotEquals(soap_addr,soap_addr3)
            self.assertNotEquals(soap_addr,soap_addr4)
            self.assertNotEquals(soap_addr,soap_addr5)

        @uses_module(ServerSOAP)
        def test_soap_create_client_errors(self):

            addr = SOAPAddress.Address("123.123.123.123:8080@network1")

            csoap = SOAPAddress.ClientSOAP
            fake_client_soap_module = FakeClientSOAPModule()
            SOAPAddress.ClientSOAP = fake_client_soap_module

            self.assertRaises(
                    ProtocolExceptions.ClientClassCreationException,
                    addr.create_client,
                    ('method1','method2')
                )

            FakeClientSOAPModule.fail = False
            self.assertRaises(
                    ProtocolExceptions.ClientInstanciationException,
                    addr.create_client,
                    ('method1','method2')
                )

            SOAPAddress.ClientSOAP = csoap
            

        @uses_module(ServerSOAP)
        def test_soap_create_client(self):
            message2 = self.message2

            cfg_manager= ConfigurationManager.ConfigurationManager()
            cfg_manager.append_module(configuration_module)

            soap_server_class = ServerSkel.factory(cfg_manager, Protocols.SOAP,self.methods)

            class SoapServerClass(soap_server_class):
                def do_say_hello(self,msg):
                    return msg + message2

            soap_server_instance = SoapServerClass(
                    SOAP = ('',self.port)
                )
            soap_server_instance.start()
            
            soap_addr = SOAPAddress.Address(
                    self.host + ':' + str(self.port) + '@NetworkA'
                )
            
            soap_client = soap_addr.create_client(self.methods)
            self.assertEquals(
                soap_client.say_hello(self.message1),
                self.message1 + message2
            )
            soap_server_instance.stop()

            soap_addr = SOAPAddress.Address(
                    self.host + ':' + str(self.port) + '@NetworkA'
                )
    else:
        print >> sys.stderr, "SOAPAddressTestCase skipped; SOAPpy not installed"

def suite():
    return unittest.makeSuite(SOAPAddressTestCase)

if __name__ == '__main__':
    unittest.main()

