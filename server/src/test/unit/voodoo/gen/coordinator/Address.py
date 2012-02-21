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


import voodoo.gen.coordinator.Address as Address
import voodoo.gen.exceptions.coordinator.AccessExceptions as AccessExceptions

class ImplementorClass(Address.IpBasedAddress):
    def create_client(self,methods):
        return None
    def get_protocol(self):
        pass
    def __cmp__(self,other):
        return Address.IpBasedAddress._compare(self,other)
    def __eq__(self, other):
        return self.__cmp__(other) == 0
    def __ne__(self, other):
        return self.__cmp__(other) != 0

class AddressImplementorClass(Address.Address):
    def __init__(self,address):
        Address.Address.__init__(self)
        self._address = address
    def _get_address(self):
        return self._address
    def create_client(self, methods):
        pass
    def get_protocol(self):
        pass
    def __cmp__(self,other):
        pass
    def __eq__(self,other):
        pass
    def __ne__(self, other):
        pass

class AddressTestCase(unittest.TestCase):
    def test_address(self):
        self.assertRaises(
                TypeError,
                Address.Address
            )
        addr = 'my address'
        address = AddressImplementorClass(addr)
        self.assertEquals(
            addr,
            address.address
        )


    def test_ip_based_address(self):
        valid_addresses   = (
                '127.0.0.1:8080@Network1',
                'localhost:10000@Network2',
                'localhost:65535@Network2'
            )
        invalid_addresses = (
                'A',
                '127.0.0.1@Network1',
                '127.0.0.1:-1@Network1',
                '127.0.0.1:65536@Network1',
                ':8080@Network1',
                '127.0.0.1:@Network2',
                '127.0.0.1:8080@'
            )

        self.assertRaises(
                TypeError,
                Address.IpBasedAddress,
                valid_addresses[0]
            )


        for i in valid_addresses:
            # No problem
            ImplementorClass(i)

        for i in invalid_addresses:
            self.assertRaises(
                AccessExceptions.AccessInvalidIpBasedFormat,
                ImplementorClass,
                i
            )

        for i in valid_addresses:
            address1 = ImplementorClass(i)
            address2 = ImplementorClass(i)
            self.assertEquals(address1,address2)
            for j in valid_addresses:
                if i != j:
                    address3 = ImplementorClass(j)
                    self.assertNotEquals(
                            address1,
                            address3
                        )



def suite():
    return unittest.makeSuite(AddressTestCase)

if __name__ == '__main__':
    unittest.main()

