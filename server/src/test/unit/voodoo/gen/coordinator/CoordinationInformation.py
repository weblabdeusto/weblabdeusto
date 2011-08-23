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
import StringIO

import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.coordinator.CoordinationInformation as CoordInfo
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.coordinator.Access as Access
import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.exceptions.coordinator.CoordinatorExceptions as CoordExceptions

import voodoo.gen.protocols.Direct.Network as DirectNetwork
import voodoo.gen.protocols.Direct.Address as DirectAddress
import voodoo.gen.protocols.SOAP.Network as SOAPNetwork
import voodoo.gen.protocols.SOAP.Address as SOAPAddress

import voodoo.lock as lock

import test.unit.voodoo.gen.coordinator.SampleServerType as ServerType

class CoordinationInformationTestCase(unittest.TestCase):
    
    def test_coord_machine(self):
        map = CoordInfo.CoordinationMap()

        #Creators
        map.add_new_machine('machine')
        map.add_new_instance('machine','instance')
        map.add_new_server(
                'machine',
                'instance',
                'server1',
                ServerType.Login,
                ()
            )
        
        #Basic __getitem__
        machine     = map['machine']
        instance    = machine['instance']
        server1     = instance['server1']

        #parents
        self.assertEquals(machine.parent,   map)
        self.assertEquals(instance.parent,  machine)
        self.assertEquals(server1.parent,   instance)
    
        #addresses
        machine_address = CoordAddress.CoordAddress(
                    'machine'
                )
        
        instance_address = CoordAddress.CoordAddress(
                    'machine',
                    'instance'
                )
        server_address = CoordAddress.CoordAddress(
                    'machine',
                    'instance',
                    'server1'
                )
    
        self.assertEquals(machine.address,  machine_address)
        self.assertEquals(instance.address, instance_address)
        self.assertEquals(server1.address,  server_address)
        
        # machine's __getitem__
        self.assertEquals(machine[server_address],server1)
        self.assertEquals(machine['instance'],instance)
        self.assertEquals(
                machine[server_address.get_instance_address()],
                instance
            )
    
        # instance's __getitem__
        self.assertEquals(instance['server1'],server1)
        self.assertEquals(instance[server_address],server1)
        
    def test_iterators(self):
        map = CoordInfo.CoordinationMap()

        #Creators
        map.add_new_machine('machine')
        map.add_new_instance('machine','instance')
        map.add_new_server(
                'machine',
                'instance',
                'server1',
                ServerType.Login,
                ()
            )
        

        machine     = map['machine']
        instance    = machine['instance']
        server1     = instance['server1']
        
        y = instance.get_servers()
        
        next = y.next()
        self.assertEquals(next,server1)
        
        map.add_new_server(
                'machine',
                'instance',
                'server2',
                ServerType.Login,
                ()
            )
        server2     = instance['server2']

        next = y.next()
        self.assertEquals(next,server2)
        self.assertRaises(StopIteration,y.next)
    
    def test_map_operations(self):
        map = CoordInfo.CoordinationMap()
        map.add_new_machine('machine')
        map.add_new_instance('machine','instance')
        map.add_new_server(
                'machine',
                'instance',
                'server1',
                ServerType.Login,
                ()
            )

        machine  = map['machine']
        instance = machine['instance']
        server1  = instance['server1']
        
        
        
        self.assertEquals(server1.status,False)

        server1_copy = server1.copy()
        map.set_status('machine','instance','server1',True)
        
        self.assertEquals(server1.status,True)
        self.assertEquals(server1_copy.status,False)

    def test_accesses(self):
        # Create map, machine and instance
        map = CoordInfo.CoordinationMap()
        map.add_new_machine('machine')
        map.add_new_instance('machine','instance')
        # Create servers
        map.add_new_server(
                'machine',
                'instance',
                'server1',
                ServerType.Login,
                ()
            )
        map.add_new_server(
                'machine',
                'instance',
                'server2',
                ServerType.Login,
                ()
            )
        
        # Create accesses for server1

        # 1st: address
        server1_address = map['machine']['instance']['server1'].address

        # 2nd: network
        server1_direct_address = DirectAddress.from_coord_address(server1_address)
        server1_direct_network = DirectNetwork.DirectNetwork(server1_direct_address)
        
        # 3rd: access
        access1_direct = Access.Access(
                    Protocols.Direct,
                    AccessLevel.instance,
                    (server1_direct_network,)
                )
    
        # 1st: address
        server1_ip_address1 = SOAPAddress.Address(
                '192.168.0.1:8080@NETWORK1'
            )
        # 2nd: network
        server1_soap_network1 = SOAPNetwork.SOAPNetwork(
                server1_ip_address1
            )
        
        # 1st: address
        server1_ip_address2 = SOAPAddress.Address(
                '130.206.137.60:8080@NETWORK2'
            )
        
        # 2nd: network
        server1_soap_network2 = SOAPNetwork.SOAPNetwork(
                server1_ip_address2
            )
        
        # access (with two networks)
        access1_soap = Access.Access(
                    Protocols.SOAP,
                    AccessLevel.network,
                    (
                        server1_soap_network1,
                        server1_soap_network2
                    )
                )

        # append accesses to the server
        map.append_accesses('machine', 'instance', 'server1',
                ( 
                    access1_direct,
                    access1_soap
                )
            )
        
        # Same with the other server
        server2_address = map['machine']['instance']['server2'].address
        server2_direct_address = DirectAddress.from_coord_address(server2_address)
        server2_direct_network = DirectNetwork.DirectNetwork(server2_direct_address)
    
        
        access2_direct = Access.Access(
                    Protocols.Direct,
                    AccessLevel.instance,
                    (server2_direct_network,)
                )

        # 1st: address
        server2_ip_address1 = SOAPAddress.Address(
                '192.168.0.2:8080@NETWORK1'
            )
        # 2nd: network
        server2_soap_network1 = SOAPNetwork.SOAPNetwork(
                server2_ip_address1
            )
        
        # 1st: address
        server2_ip_address2 = SOAPAddress.Address(
                '130.206.137.61:8080@NETWORK3'
            )
        
        # 2nd: network
        server2_soap_network2 = SOAPNetwork.SOAPNetwork(
                server2_ip_address2
            )

        access2_soap = Access.Access(
                    Protocols.SOAP,
                    AccessLevel.network,
                    (
                        server2_soap_network1,
                        server2_soap_network2
                    )
                )
        
        map.append_accesses('machine', 'instance', 'server2',
                ( 
                    access2_direct,
                    access2_soap
                )
            )
        
        # Now, check results
        
        server1 = map[server1_address]
        server2 = map[server2_address]

        networks = server1.can_connect(server2)
        # There should be only 2 networks (130.206.137.61:8080@NETWORK3 is 
        # at NETWORK3, which is different to 130.206.137.60)
        self.assertEquals(len(networks),2)
        # First one: the direct one
        self.assertEquals(networks[0].address.address,'server2:instance@machine')
        # Second one: the network one
        self.assertEquals(networks[1].address.address,'192.168.0.2:8080')
        
        # Let's try exceptions...
        
        # Machine does not exist
        self.assertRaises(
                CoordExceptions.CoordMachineNotFound,
                map.add_new_instance,
                'machine_not_exists',
                'instanceX'
            )
        
        # Instance does not exist
        self.assertRaises(
                CoordExceptions.CoordInstanceNotFound,
                map.add_new_server,
                'machine',
                'instance_not_exists',
                'server',
                ServerType.Login,
                ()
            )
        
        # Server does not exist
        self.assertRaises(
                CoordExceptions.CoordServerNotFound,
                map.append_accesses,
                'machine',
                'instance',
                'server_not_exists',
                ()
            )
        
        # Invalid key
        self.assertRaises(
                CoordExceptions.CoordInvalidKey, 
                lambda : map[5])

        self.assertRaises(CoordExceptions.CoordInvalidKey, 
                lambda : map['machine'][5])
        
        self.assertRaises(CoordExceptions.CoordInvalidKey, 
                lambda : map['machine']['instance'][5])

        # And that's all :-)
        

    def test_get_servers(self):
        # Create map, machine and instance
        map = CoordInfo.CoordinationMap()


        # Create servers

        # There are gonna be:
        # 2 machines, each machine with:
        # 2 instances, each instance with:
        # 2 servers, one of Login, the other of Coordinator. each one has:
        # 2 protocols
        #
        # 1st protocol) direct network
        # 2nd protocol) SOAP network, with IP number:
        #       192.168.0.$(machine_number):$(PORT):NETWORK
        #

        for machine_num in range(2):
            map.add_new_machine('machine' + str(machine_num))
            for instance_num in range(2):
                map.add_new_instance(
                        'machine' + str(machine_num),
                        'instance' + str(instance_num)
                    )
                for server_num in range(2):
                    if server_num % 2 == 0:
                        server_type = ServerType.Login
                    else:
                        server_type = ServerType.Coordinator
                        
                    map.add_new_server(
                        'machine' + str(machine_num),
                        'instance' + str(instance_num),
                        'server' + str(server_num),
                        server_type,
                        ()
                    )
                    # 1st: address
                    address = map['machine' + str(machine_num)
                        ]['instance' + str(instance_num)
                        ]['server' + str(server_num)
                        ].address
                    # 2nd: network
                    dir_addr = DirectAddress.from_coord_address(address)
                    network = DirectNetwork.DirectNetwork(
                        dir_addr
                    )
        
                    # 3rd: access
                    access_direct = Access.Access(
                                Protocols.Direct,
                                AccessLevel.instance,
                                (network,)
                            )
                    # 1st: address
                    server_ip_address1 = SOAPAddress.Address(
                        '192.168.0.%i:%i@NETWORK'
                        % ( 
                            machine_num + 1,
                            8000 + machine_num * 100
                            + instance_num * 10 
                            + server_num
                        )
                    )
                    # 2nd: network
                    server_soap_network1 = SOAPNetwork.SOAPNetwork(
                        server_ip_address1
                    )
        
                    # access
                    access_soap = Access.Access(
                            Protocols.SOAP,
                            AccessLevel.network,
                            (
                                server_soap_network1,
                            )
                        )

                    # append accesses to the server
                    map.append_accesses(
                        'machine' + str(machine_num), 
                        'instance' + str(instance_num), 
                        'server' + str(server_num),
                        ( 
                            access_direct,
                            access_soap
                        )
                    )

        server = map['machine1']['instance0']['server0']
        it = map.get_servers(server,ServerType.Coordinator)
        
        server,networks  = it.next()
        self.assertEquals(server,map['machine1']['instance0']['server1'])
        self.assertEquals(len(networks),2)
        self.assertEquals(
                networks[0].address.address,
                'server1:instance0@machine1'
            )
        self.assertEquals(
                networks[1].address.address,
                '192.168.0.2:8101'
            )
        
        server,networks  = it.next()
        self.assertEquals(server,map['machine1']['instance1']['server1'])
        self.assertEquals(len(networks),1)
        self.assertEquals(
                networks[0].address.address,
                '192.168.0.2:8111'
            )
        
        server,networks  = it.next()
        self.assertEquals(server,map['machine0']['instance0']['server1'])
        self.assertEquals(len(networks),1)
        self.assertEquals(
                networks[0].address.address,
                '192.168.0.1:8001'
            )
    
        server,networks  = it.next()
        self.assertEquals(len(networks),1)
        self.assertEquals(server,map['machine0']['instance1']['server1'])
        self.assertEquals(
                networks[0].address.address,
                '192.168.0.1:8011'
            )
        
        self.assertRaises(StopIteration,it.next)
    
    def test_store_and_load_methods(self):
        map = CoordInfo.CoordinationMap()
        c = CoordInfo.CoordinationMapController(map)
        map.add_new_machine('machine')
        map.add_new_instance('machine','instance')
        map.add_new_server(
                'machine',
                'instance',
                'server1',
                ServerType.Login,
                ()
            )
        where = StringIO.StringIO()
        c.store(where)
        c2 = CoordInfo.CoordinationMapController()
        where2 = StringIO.StringIO(where.getvalue())
        c2.load(where2)
        # If this works, everything seems to work :-)
        machine   = c2._map['machine']
        instance  = machine['instance']
        server    = instance['server1']
        server_type_name = server.server_type.name
        self.assertEquals(
                server_type_name,
                'Login'
            )
        # Let's check locks, too
        the_lock = server._accesses_lock
        self.assertEquals(
                type(the_lock),
                lock.RWLock
            )
    
    def test_errors_on_getitems(self):
        map = CoordInfo.CoordinationMap()
        map.add_new_machine('machine')
        map.add_new_instance('machine','instance')
        map.add_new_server(
                'machine',
                'instance',
                'server1',
                ServerType.Login,
                ()
            )
        self.assertRaises(
            CoordExceptions.CoordMachineNotFound,
            map.__getitem__,
            'whatever'
        )
        self.assertRaises(
            CoordExceptions.CoordInstanceNotFound,
            map['machine'].__getitem__,
            'whatever'
        )
        self.assertRaises(
            CoordExceptions.CoordServerNotFound,
            map['machine']['instance'].__getitem__,
            'whatever'
        )


    
def suite():
    return unittest.makeSuite(CoordinationInformationTestCase)

if __name__ == '__main__':
    unittest.main()

