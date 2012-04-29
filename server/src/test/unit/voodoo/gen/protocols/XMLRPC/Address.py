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

import voodoo.gen.protocols.XMLRPC.Address as XMLRPCAddress
import voodoo.gen.protocols.XMLRPC.server as ServerXMLRPC

import voodoo.gen.generators.ServerSkel as ServerSkel
import voodoo.gen.protocols.protocols as Protocols

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import voodoo.gen.exceptions.protocols.ProtocolErrors as ProtocolErrors

class FakeClientClass(object):
    def __init__(self, *args):
        raise Exception("bar")

class FakeClientXMLRPCModule(object):
    fail = True

    @staticmethod
    def generate(methods):
        if FakeClientXMLRPCModule.fail:
            raise Exception("foo")
        else:
            return FakeClientClass

class XMLRPCAddressTestCase(unittest.TestCase):
    def setUp(self):
        self.methods = ['say_hello']
        self.message1 = "hello"
        self.message2 = "olleh"
        self.host = 'localhost'
        self.port = 10001

    def test_equals(self):
        xmlrpc_addr = XMLRPCAddress.Address(
                self.host + ':' + str(self.port) + '@NetworkA'
            )
        xmlrpc_addr2 = XMLRPCAddress.Address(
                self.host + ':' + str(self.port) + '@NetworkA'
            )
        xmlrpc_addr3 = XMLRPCAddress.Address(
                self.host + ':' + str(self.port) + '@NetworkB'
            )
        xmlrpc_addr4 = XMLRPCAddress.Address(
                self.host + ':' + str(self.port+1) + '@NetworkA'
            )
        xmlrpc_addr5 = XMLRPCAddress.Address(
                self.host +'.' + ':' + str(self.port) + '@NetworkA'
            )
        self.assertEquals(xmlrpc_addr,xmlrpc_addr2)
        self.assertNotEquals(xmlrpc_addr,xmlrpc_addr3)
        self.assertNotEquals(xmlrpc_addr,xmlrpc_addr4)
        self.assertNotEquals(xmlrpc_addr,xmlrpc_addr5)

    @uses_module(ServerXMLRPC)
    def test_xmlrpc_create_client_errors(self):

        addr = XMLRPCAddress.Address("123.123.123.123:8080@network1")

        cxmlrpc = XMLRPCAddress.ClientXMLRPC
        fake_client_xmlrpc_module = FakeClientXMLRPCModule()
        XMLRPCAddress.ClientXMLRPC = fake_client_xmlrpc_module

        self.assertRaises(
                ProtocolErrors.ClientClassCreationError,
                addr.create_client,
                ('method1','method2')
            )

        FakeClientXMLRPCModule.fail = False
        self.assertRaises(
                ProtocolErrors.ClientInstanciationError,
                addr.create_client,
                ('method1','method2')
            )

        XMLRPCAddress.ClientXMLRPC = cxmlrpc


    @uses_module(ServerXMLRPC)
    def test_xmlrpc_create_client(self):
        message2 = self.message2

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        xmlrpc_server_class = ServerSkel.factory(cfg_manager,Protocols.XMLRPC,self.methods)

        class XmlRpcServerClass(xmlrpc_server_class):
            def do_say_hello(self,msg):
                return msg + message2

        xmlrpc_server_instance = XmlRpcServerClass(
                XMLRPC = ('',self.port)
            )
        xmlrpc_server_instance.start()

        xmlrpc_addr = XMLRPCAddress.Address(
                self.host + ':' + str(self.port) + '@NetworkA'
            )

        xmlrpc_client = xmlrpc_addr.create_client(self.methods)
        self.assertEquals(
            xmlrpc_client.say_hello(self.message1),
            self.message1 + message2
        )
        xmlrpc_server_instance.stop()

        xmlrpc_addr = XMLRPCAddress.Address(
                self.host + ':' + str(self.port) + '@NetworkA'
            )

def suite():
    return unittest.makeSuite(XMLRPCAddressTestCase)

if __name__ == '__main__':
    unittest.main()

