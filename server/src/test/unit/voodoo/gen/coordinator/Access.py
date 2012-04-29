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

import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.coordinator.Access as Access
import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.coordinator.AccessErrors as AccessErrors

import voodoo.gen.protocols.Direct.network as DirectNetwork
import voodoo.gen.protocols.Direct.Address as DirectAddress
import voodoo.gen.protocols.SOAP.network as SOAPNetwork
import voodoo.gen.protocols.SOAP.Address as SOAPAddress



class AccessTestCase(unittest.TestCase):
    def test_direct_accesses(self):
        coord_address1 = CoordAddress.CoordAddress.translate_address(
                'server:instance@machine'
            )

        coord_address2 = CoordAddress.CoordAddress.translate_address(
                'server2:instance@machine'
            )

        coord_address3 = CoordAddress.CoordAddress.translate_address(
                'server:instance2@machine'
            )

        direct_address1 = DirectAddress.from_coord_address(coord_address1)
        direct_address2 = DirectAddress.from_coord_address(coord_address2)
        direct_address3 = DirectAddress.from_coord_address(coord_address3)

        direct_network1 = DirectNetwork.DirectNetwork(direct_address1)
        direct_network2 = DirectNetwork.DirectNetwork(direct_address2)
        direct_network3 = DirectNetwork.DirectNetwork(direct_address3)

        a1 = Access.Access(Protocols.Direct,AccessLevel.instance,
                (direct_network1,)
            )
        a2 = Access.Access(Protocols.Direct,AccessLevel.instance,
                (direct_network2,)
            )
        a3 = Access.Access(Protocols.Direct,AccessLevel.instance,
                (direct_network3,)
            )

        self.assertEquals(a1.possible_connections(a2)[0],direct_network2)
        self.assertEquals(a2.possible_connections(a1)[0],direct_network1)

        self.assertEquals(len(a1.possible_connections(a3)),0)
        self.assertEquals(len(a2.possible_connections(a3)),0)
        self.assertEquals(len(a3.possible_connections(a1)),0)
        self.assertEquals(len(a3.possible_connections(a2)),0)

    def test_soap_accesses(self):
        ip_addr1 = '192.168.1.1:8080@net1'
        ip_addr2 = '192.168.1.2:8080@net1'
        ip_addr3 = '192.168.2.1:8080@net2'

        self.assertRaises(
            AccessErrors.AccessNotAnIpAddressError,
            SOAPNetwork.SOAPNetwork,
            'not an IpAddressError'
        )

        addr1 = SOAPAddress.Address(ip_addr1)
        addr2 = SOAPAddress.Address(ip_addr2)
        addr3 = SOAPAddress.Address(ip_addr3)

        soap_network1 = SOAPNetwork.SOAPNetwork(addr1)
        soap_network2 = SOAPNetwork.SOAPNetwork(addr2)
        soap_network3 = SOAPNetwork.SOAPNetwork(addr3)

        a1 = Access.Access(Protocols.SOAP,AccessLevel.network,
                (soap_network1,)
            )
        a2 = Access.Access(Protocols.SOAP,AccessLevel.network,
                (soap_network2,)
            )
        a3 = Access.Access(Protocols.SOAP,AccessLevel.network,
                (soap_network3,)
            )

        self.assertEquals(a1.possible_connections(a2)[0],soap_network2)
        self.assertEquals(a2.possible_connections(a1)[0],soap_network1)

        self.assertEquals(len(a1.possible_connections(a3)),0)
        self.assertEquals(len(a2.possible_connections(a3)),0)
        self.assertEquals(len(a3.possible_connections(a1)),0)
        self.assertEquals(len(a3.possible_connections(a2)),0)



def suite():
    return unittest.makeSuite(AccessTestCase)

if __name__ == '__main__':
    unittest.main()

