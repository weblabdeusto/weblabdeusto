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
import threading

import weblab.configuration_doc as configuration_doc

import test.unit.configuration as configuration_module

import test.unit.voodoo.gen.coordinator.SampleServerType as SampleServerType

import voodoo.configuration as ConfigurationManager

import voodoo.sessions.memory as SessionMemoryGateway

import voodoo.gen.coordinator.CoordinationInformation as CoordInfo
import voodoo.gen.coordinator.Access as Access
import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.coordinator.CoordinatorServer as CoordinatorServer

import voodoo.gen.exceptions.coordinator.CoordinatorServerErrors as CoordinatorServerErrors

import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.protocols.Direct.Network as DirectNetwork
import voodoo.gen.protocols.Direct.Address as DirectAddress
import voodoo.gen.protocols.SOAP.Network as SOAPNetwork
import voodoo.gen.protocols.SOAP.Address as SOAPAddress

def create_coordinator_map():
    map = CoordInfo.CoordinationMap()

    login_t = SampleServerType.Login
    map.add_new_machine ('machine0')
    map.add_new_instance('machine0','instance0')
    map.add_new_server  ('machine0','instance0','server0',login_t,())
    map.add_new_server  ('machine0','instance0','server1',login_t,())

    map.add_new_instance('machine0','instance1')
    map.add_new_server  ('machine0','instance1','server0',login_t,())

    map.add_new_machine ('machine1')
    map.add_new_instance('machine1','instance0')
    map.add_new_server  ('machine1','instance0','server0',login_t,())

    # 4 servers
    # We are in machine0, instance0, server0

    # They all have Direct

    # 1st: address
    address1 = map['machine0']['instance0']['server0'].address
    address2 = map['machine0']['instance0']['server1'].address
    address3 = map['machine0']['instance1']['server0'].address
    address4 = map['machine1']['instance0']['server0'].address

    # 2nd: network
    direct_network1 = DirectNetwork.DirectNetwork(
        DirectAddress.from_coord_address(address1)
    )
    direct_network2 = DirectNetwork.DirectNetwork(
        DirectAddress.from_coord_address(address2)
    )
    direct_network3 = DirectNetwork.DirectNetwork(
        DirectAddress.from_coord_address(address3)
    )
    direct_network4 = DirectNetwork.DirectNetwork(
        DirectAddress.from_coord_address(address4)
    )

    # 3rd: accesses
    access_direct1 = Access.Access(
        Protocols.Direct, AccessLevel.instance,(direct_network1,)
    )
    access_direct2 = Access.Access(
        Protocols.Direct, AccessLevel.instance,(direct_network2,)
    )
    access_direct3 = Access.Access(
        Protocols.Direct, AccessLevel.instance,(direct_network3,)
    )
    access_direct4 = Access.Access(
        Protocols.Direct, AccessLevel.instance,(direct_network4,)
    )

    # 4th: appending accesses
    map.append_accesses(
        'machine0','instance0','server0',( access_direct1, )
    )
    map.append_accesses(
        'machine0','instance0','server1',( access_direct2, )
    )
    map.append_accesses(
        'machine0','instance1','server0',( access_direct3, )
    )
    map.append_accesses(
        'machine1','instance0','server0',( access_direct4, )
    )

    # They all have SOAP

    # 1st: address
    server_ip_address1 = SOAPAddress.Address('127.0.0.1:9025@NETWORK')
    server_ip_address2 = SOAPAddress.Address('127.0.0.1:9026@NETWORK')
    server_ip_address3 = SOAPAddress.Address('127.0.0.1:9027@NETWORK')
    server_ip_address4 = SOAPAddress.Address('127.0.0.1:9028@NETWORK')

    # 2nd: network
    soap_network1 = SOAPNetwork.SOAPNetwork(server_ip_address1)
    soap_network2 = SOAPNetwork.SOAPNetwork(server_ip_address2)
    soap_network3 = SOAPNetwork.SOAPNetwork(server_ip_address3)
    soap_network4 = SOAPNetwork.SOAPNetwork(server_ip_address4)

    # 3rd: accesses
    access_soap1 = Access.Access(
        Protocols.SOAP,AccessLevel.network, ( soap_network1, )
    )
    access_soap2 = Access.Access(
        Protocols.SOAP,AccessLevel.network, ( soap_network2, )
    )
    access_soap3 = Access.Access(
        Protocols.SOAP,AccessLevel.network, ( soap_network3, )
    )
    access_soap4 = Access.Access(
        Protocols.SOAP,AccessLevel.network, ( soap_network4, )
    )

    # 4th: appending accesses
    map.append_accesses(
        'machine0','instance0','server0',( access_soap1, )
    )
    map.append_accesses(
        'machine0','instance0','server1',( access_soap2, )
    )
    map.append_accesses(
        'machine0','instance1','server0',( access_soap3, )
    )
    map.append_accesses(
        'machine1','instance0','server0',( access_soap4, )
    )
    return map



class CoordinatorServerTestCase(unittest.TestCase):
    def test_error(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        self.assertRaises(
                CoordinatorServerErrors.BothMapAndMapFileProvidedError,
                CoordinatorServer.CoordinatorServer,
                cfg_manager,
                map      = ":-)",
                map_file = ":-("
            )
        self.assertRaises(
                CoordinatorServerErrors.NeitherMapNorFileProvidedError,
                CoordinatorServer.CoordinatorServer,
                cfg_manager
            )

    def test_get_server(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        cfg_manager._set_value(configuration_doc.SESSION_MEMORY_GATEWAY_SERIALIZE, True)

        map = create_coordinator_map()
        coord_server = CoordinatorServer.CoordinatorServer(
                cfg_manager,
                map
            )
        self.assertRaises(
            CoordinatorServerErrors.SessionNotFoundError,
            coord_server.do_get_server,
            "p0wn3d"
        )

        my_address = map['machine0']['instance0']['server0'].address

        # What if there are problems serializing?
        self.assertRaises(
            CoordinatorServerErrors.CouldNotCreateSessionError,
            coord_server.do_new_query,
            threading.Lock(), SampleServerType.Login, None
        )

        # Ok, let's create a good one. Actually, let's do it three times
        for i in range(3):
            sess_id = coord_server.do_new_query(
                    my_address.address,SampleServerType.Login, None
                )

            cur_address = coord_server.do_get_server(sess_id)
            self.assertEquals(
                True,
                isinstance(cur_address,DirectAddress.Address)
            )
            self.assertEquals(cur_address.machine_id,  'machine0')
            self.assertEquals(cur_address.instance_id, 'instance0')
            self.assertEquals(cur_address.server_id,   'server1')

            cur_address = coord_server.do_get_server(sess_id)
            self.assertEquals(
                True,
                isinstance(cur_address,SOAPAddress.Address)
            )
            self.assertEquals(cur_address.ip_address, '127.0.0.1')
            self.assertEquals(cur_address.net_name,   'NETWORK')
            self.assertEquals(cur_address.port,       9026)

            cur_address = coord_server.do_get_server(sess_id)
            self.assertEquals(
                True,
                isinstance(cur_address,SOAPAddress.Address)
            )
            self.assertEquals(cur_address.ip_address, '127.0.0.1')
            self.assertEquals(cur_address.net_name,   'NETWORK')
            self.assertEquals(cur_address.port,       9027)

            cur_address = coord_server.do_get_server(sess_id)
            self.assertEquals(
                True,
                isinstance(cur_address,SOAPAddress.Address)
            )
            self.assertEquals(cur_address.ip_address, '127.0.0.1')
            self.assertEquals(cur_address.net_name,   'NETWORK')
            self.assertEquals(cur_address.port,       9028)

            # There are no more servers!
            self.assertRaises(
                CoordinatorServerErrors.NoServerFoundError,
                coord_server.do_get_server,
                sess_id
            )

    def test_get_all_servers(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        map = create_coordinator_map()
        coord_server = CoordinatorServer.CoordinatorServer(
                cfg_manager,
                map
            )

        my_address = map['machine0']['instance0']['server0'].address

        everything = coord_server.do_get_all_servers(
                my_address.address,SampleServerType.Login, None
            )

        self.assertEquals(
                3,
                len(everything)
            )

        server0, networks0 = everything[0]
        server1, networks1 = everything[1]
        server2, networks2 = everything[2]

        # everything[0]
        cur_address = networks0[0].address
        self.assertEquals(
            True,
            isinstance(cur_address,DirectAddress.Address)
        )

        self.assertEquals(cur_address.machine_id,  'machine0')
        self.assertEquals(cur_address.instance_id, 'instance0')
        self.assertEquals(cur_address.server_id,   'server1')

        cur_address = networks0[1].address
        self.assertEquals(
            True,
            isinstance(cur_address,SOAPAddress.Address)
        )
        self.assertEquals(cur_address.ip_address, '127.0.0.1')
        self.assertEquals(cur_address.net_name,   'NETWORK')
        self.assertEquals(cur_address.port,       9026)

        # everything[1]
        cur_address = networks1[0].address
        self.assertEquals(
            True,
            isinstance(cur_address,SOAPAddress.Address)
        )
        self.assertEquals(cur_address.ip_address, '127.0.0.1')
        self.assertEquals(cur_address.net_name,   'NETWORK')
        self.assertEquals(cur_address.port,       9027)

        # everything[2]
        cur_address = networks2[0].address
        self.assertEquals(
            True,
            isinstance(cur_address,SOAPAddress.Address)
        )
        self.assertEquals(cur_address.ip_address, '127.0.0.1')
        self.assertEquals(cur_address.net_name,   'NETWORK')
        self.assertEquals(cur_address.port,       9028)

        # Trying something that there is no server
        everything = coord_server.do_get_all_servers(
                my_address.address,SampleServerType.YetAnother, None
            )
        self.assertEquals(everything, [])

    def test_get_networks(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        map = create_coordinator_map()
        coord_server = CoordinatorServer.CoordinatorServer(
                cfg_manager,
                map
            )

        my_address = map['machine0']['instance0']['server0'].address

        other_address1 = map['machine0']['instance0']['server1'].address
        other_address2 = map['machine0']['instance1']['server0'].address
        other_address3 = map['machine1']['instance0']['server0'].address

        # other_address1
        networks1 = coord_server.do_get_networks(
                my_address,
                other_address1
            )

        self.assertEquals(
                2,
                len(networks1)
            )

        cur_address = networks1[0].address
        self.assertEquals(
            True,
            isinstance(cur_address,DirectAddress.Address)
        )
        self.assertEquals(cur_address.server_id,   'server1')
        self.assertEquals(cur_address.instance_id, 'instance0')
        self.assertEquals(cur_address.machine_id,  'machine0')

        cur_address = networks1[1].address
        self.assertEquals(
            True,
            isinstance(cur_address,SOAPAddress.Address)
        )
        self.assertEquals(cur_address.ip_address, '127.0.0.1')
        self.assertEquals(cur_address.net_name,   'NETWORK')
        self.assertEquals(cur_address.port,       9026)

        # other_address2
        networks2 = coord_server.do_get_networks(
                my_address,
                other_address2
            )

        cur_address = networks2[0].address
        self.assertEquals(
            True,
            isinstance(cur_address,SOAPAddress.Address)
        )
        self.assertEquals(cur_address.ip_address, '127.0.0.1')
        self.assertEquals(cur_address.net_name,   'NETWORK')
        self.assertEquals(cur_address.port,       9027)

        # other_address3
        networks3 = coord_server.do_get_networks(
                my_address,
                other_address3
            )

        cur_address = networks3[0].address
        self.assertEquals(
            True,
            isinstance(cur_address,SOAPAddress.Address)
        )
        self.assertEquals(cur_address.ip_address, '127.0.0.1')
        self.assertEquals(cur_address.net_name,   'NETWORK')
        self.assertEquals(cur_address.port,       9028)

def suite():
    return unittest.makeSuite(CoordinatorServerTestCase)

if __name__ == '__main__':
    unittest.main()

