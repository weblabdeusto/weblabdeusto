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


import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.protocols.Direct.Address as DirectAddress
import voodoo.gen.protocols.Direct.Exceptions as DirectExceptions

import voodoo.gen.generators.ServerSkel as ServerSkel

import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions
import voodoo.gen.protocols.protocols as Protocols

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

class DirectAddressTestCase(unittest.TestCase):
    def setUp(self):
        self.methods = ['say_hello']
        self.message1 = "hello"
        self.message2 = "olleh"
        self.machine_id = 'machine_id_sample'
        self.instance_id = 'instance_id_sample'
        self.server_id = "server_id_sample"

    def test_address_constructor(self):
        machine_id  = 'a'
        instance_id = 'b'
        server_id   = 'c'
        addr = DirectAddress.Address(
                machine_id,
                instance_id,
                server_id
            )

        self.assertEquals(
                addr.machine_id,
                machine_id
            )

        self.assertEquals(
                addr.instance_id,
                instance_id
            )

        self.assertEquals(
                addr.server_id,
                server_id
            )

    def test_bad_address_constructors(self):
        machine_id  = 'a'
        instance_id = 'b'
        server_id   = 'c'
        self.assertRaises(
                DirectExceptions.InvalidArgumentAddressException,
                DirectAddress.Address,
                5,
                instance_id,
                server_id
            )
        self.assertRaises(
                DirectExceptions.InvalidArgumentAddressException,
                DirectAddress.Address,
                machine_id,
                5,
                server_id
            )
        self.assertRaises(
                DirectExceptions.InvalidArgumentAddressException,
                DirectAddress.Address,
                machine_id,
                instance_id,
                5
            )

    def test_from_coord_address(self):
        machine_id  = 'a'
        instance_id = 'b'
        server_id   = 'c'
        
        coordAddress = CoordAddress.CoordAddress(
                machine_id,
                instance_id,
                server_id
            )

        addr = DirectAddress.from_coord_address(coordAddress)
        
        self.assertEquals(
                addr.machine_id,
                machine_id
            )
        self.assertEquals(
                addr.instance_id,
                instance_id
            )
        self.assertEquals(
                addr.server_id,
                server_id
            )

    def test_cmp(self):
        machine_id  = 'a'
        instance_id = 'b'
        server_id   = 'c'
        
        coordAddress1 = CoordAddress.CoordAddress(
                machine_id,
                instance_id,
                server_id
            )

        coordAddress2 = CoordAddress.CoordAddress(
                machine_id + '.',
                instance_id,
                server_id
            )

        coordAddress3 = CoordAddress.CoordAddress(
                machine_id,
                instance_id + '.',
                server_id
            )

        coordAddress4 = CoordAddress.CoordAddress(
                machine_id,
                instance_id,
                server_id + '.'
            )


        addr1 = DirectAddress.from_coord_address(coordAddress1)
        addr2 = DirectAddress.from_coord_address(coordAddress1)
        addr3 = DirectAddress.from_coord_address(coordAddress2)
        addr4 = DirectAddress.from_coord_address(coordAddress3)
        addr5 = DirectAddress.from_coord_address(coordAddress4)

        self.assertEquals(addr1,addr2)
        self.assertNotEquals(addr1,addr3)
        self.assertNotEquals(addr1,addr4)
        self.assertNotEquals(addr1,addr5)
    
    def test_bad_from_coord_address(self):
        self.assertRaises(
                DirectExceptions.NotACoordAddressException,
                DirectAddress.from_coord_address,
                5
            )
    
    def test_direct_create_client(self):
        message2 = self.message2

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        direct_server_class = ServerSkel.factory(cfg_manager, Protocols.Direct,self.methods)

        class DirectServerClass(direct_server_class):
            def do_say_hello(self,msg):
                return msg + message2

        DirectServerClass(
                Direct = (self.server_id,)
            )

        direct_addr = DirectAddress.Address(
                    self.machine_id,
                    self.instance_id,
                    self.server_id
                )
        direct_client = direct_addr.create_client(self.methods)
        self.assertEquals(
            direct_client.say_hello(self.message1),
            self.message1 + message2
        )
    
    def test_bad_client_creation(self):
        message2 = self.message2
        direct_addr = DirectAddress.Address(
                self.machine_id,
                self.instance_id,
                'wrong_server_id'
            )
        self.assertRaises(
            ProtocolExceptions.ClientCreationException,
            direct_addr.create_client,
            self.methods
        )

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        direct_server_class = ServerSkel.factory(cfg_manager, Protocols.Direct,self.methods)

        class DirectServerClass(direct_server_class):
            def do_say_hello(self,msg):
                return msg + message2

        DirectServerClass(
                Direct = (self.server_id,)
            )

        direct_addr = DirectAddress.Address(
                self.machine_id,
                self.instance_id,
                self.server_id
            )

        self.assertRaises(
            ProtocolExceptions.ClientClassCreationException,
            direct_addr.create_client,
            'not valid methods'
        )

    
def suite():
    return unittest.makeSuite(DirectAddressTestCase)

if __name__ == '__main__':
    unittest.main()

