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
import random

from test.util.module_disposer import uses_module

import voodoo.gen.coordinator.CoordinatorServer as CoordinatorServer
import voodoo.gen.coordinator.CoordinationInformation as CoordInfo
import voodoo.gen.coordinator.Access as Access
import voodoo.gen.coordinator.AccessLevel as AccessLevel

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import voodoo.gen.locator.ServerLocator as ServerLocator
import voodoo.gen.locator.ServerTypeHandler as ServerTypeHandler

import voodoo.gen.exceptions.locator.LocatorExceptions as LocatorExceptions
import voodoo.gen.exceptions.coordinator.CoordinatorServerExceptions as CoordinatorServerExceptions
import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

import voodoo.gen.generators.ServerSkel as ServerSkel

import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.protocols.Direct.Address as DirectAddress
import voodoo.gen.protocols.Direct.Network as DirectNetwork
import voodoo.gen.protocols.SOAP.Address    as SOAPAddress
import voodoo.gen.protocols.SOAP.Network    as SOAPNetwork
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP

import voodoo.gen.registry.server_registry as ServerRegistry
import voodoo.methods as voodoo_methods

import test.unit.voodoo.gen.locator.ServerTypeSample as ServerTypeSample


import test.unit.voodoo.gen.coordinator.SampleServerType as SampleServerType

keep_returning_login_server = True
coordinator_methods = voodoo_methods.coordinator
login_methods = ['method1']

class ServerLocatorTestCase(unittest.TestCase):

    def setUp(self):
        self._machine_id  = 'machine'
        self._instance_id = 'instance'
        self._server_id   = 'coordinator_server_name'
        self._login_server1_id = 'login_server_name1'
        self._login_server2_id = 'login_server_name2'

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        self.server_type_handler = ServerTypeHandler.ServerTypeHandler(
                ServerTypeSample,
                {
                    'Login' : login_methods,
                    'Coordinator' : coordinator_methods
                }
            )

        direct_coordinator = ServerSkel.factory(
                cfg_manager,
                Protocols.Direct, coordinator_methods
            )
        class CoordinatorImplementor(direct_coordinator):
            def __init__(self,*args,**kargs):
                direct_coordinator.__init__(self,*args,**kargs)
            def do_new_query(self, address, server_type, restrictions):
                return "the session"
            def do_get_server(self, session_id):
                raise CoordinatorServerExceptions.NoServerFoundException("No server found for session_id = " + session_id)
            def do_get_all_servers(self):
                raise NotImplementedError("Not implemented get_all_servers")
            def do_get_networks(self):
                raise NotImplementedError("Not implemented get_networks")
            def do_logout(self, session_id):
                pass

        self._coordinatorImplementor = CoordinatorImplementor

        self.coordinator_server_address = DirectAddress.Address(
                self._machine_id,
                self._instance_id,
                self._server_id
            )

        self._coordinator_server = CoordinatorImplementor(
                    Direct = (
                        self.coordinator_server_address.address,
                    )
                )

        direct_login = ServerSkel.factory(
                cfg_manager,
                Protocols.Direct, login_methods
            )
        class LoginImplementor(direct_login):
            def __init__(self,*args,**kargs):
                direct_login.__init__(self,*args,**kargs)
            def do_method1(self,msg):
                return msg + " through Login Server"

        self._loginImplementor = LoginImplementor

        self.login_server1_address = DirectAddress.Address(
                self._machine_id,
                self._instance_id,
                self._login_server1_id
            )

        self.login_server2_address = DirectAddress.Address(
                self._machine_id,
                self._instance_id,
                self._login_server2_id
            )

        self._login_server1 = LoginImplementor(
                    Direct = (
                        self.login_server1_address.address,
                    )
                )

        self._login_server2 = LoginImplementor(
                    Direct = (
                        self.login_server2_address.address,
                    )
                )

    def tearDown(self):
        ServerRegistry.get_instance().clear()
    
    def _get_new_locator(self):
        return ServerLocator.ServerLocator(
            self.coordinator_server_address,
            self.server_type_handler
        )

    def _reset_locator_cache(self,locator):
        # Reset the cache
        locator._cache.clear()
        self.assertEquals(
                None,
                locator._get_server_from_cache(
                    ServerTypeSample.Login,
                    ()
                )
            )

    if ServerSOAP.SOAPPY_AVAILABLE:
        @uses_module(ServerSOAP)
        def test_with_coordinator(self):
            cfg_manager= ConfigurationManager.ConfigurationManager()
            cfg_manager.append_module(configuration_module)

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
            server_ip_address1 = SOAPAddress.Address('127.0.0.1:12345@NETWORK')
            server_ip_address2 = SOAPAddress.Address('127.0.0.1:12346@NETWORK')
            server_ip_address3 = SOAPAddress.Address('127.0.0.1:12347@NETWORK')
            server_ip_address4 = SOAPAddress.Address('127.0.0.1:12348@NETWORK')

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

            direct_coordinator = ServerSkel.factory(
                    cfg_manager,
                    (Protocols.Direct, Protocols.SOAP), coordinator_methods
                )

            class YetAnother(CoordinatorServer.CoordinatorServer,direct_coordinator):
                def __init__(self,cfg_manager,map,*args,**kargs):
                    CoordinatorServer.CoordinatorServer.__init__(self,cfg_manager,map, *args, **kargs)

            direct_login = ServerSkel.factory(
                    cfg_manager,
                    (Protocols.Direct, Protocols.SOAP), login_methods
                )
            coordinator_server_address = DirectAddress.Address(
                        "machine0",
                        "instance0",
                        "server0"
                    )

            s1= YetAnother(cfg_manager, map,Direct = (coordinator_server_address.address,), SOAP = ('',12345))
            s1.start()

            class YetAnother2(direct_login):
                def do_method1(self,arg):
                    return arg * 3
            s2 = YetAnother2( Direct = (address2.address,), SOAP = ('',12346))
            s2.start()
        
            server_type_handler = ServerTypeHandler.ServerTypeHandler(
                    SampleServerType,
                    {
                        'Login' : login_methods,
                        'Coordinator' : coordinator_methods,
                        'YetAnother' : []
                    }
                )

            locator = ServerLocator.ServerLocator(
                    coordinator_server_address,
                    server_type_handler
                )
            login_server = locator.get_server(
                    coordinator_server_address.address,
                    SampleServerType.Login,
                    None
                )

            full_name = '%s.%s' % ( login_server.__class__.__module__, login_server.__class__.__name__ )
            self.assertEquals(
                    'voodoo.gen.protocols.Direct.ClientDirect.ClientDirect',
                    full_name
                )

            msg = "hello"
            answer = login_server.method1(msg)
            self.assertEquals(
                    msg * 3,
                    answer
                )

            other_login_server = locator.get_server(
                    coordinator_server_address.address,
                    SampleServerType.Login,
                    None
                )

            # It will ask for it from the cache
            self.assertEquals(
                    login_server,
                    other_login_server
                )

            # Let's say that the login server is broken
            locator.inform_server_not_working(login_server,SampleServerType.Login,None)

            old_test_me = YetAnother2.do_test_me

            def wrong_test_me(self,arg):
                YetAnother2.do_test_me = old_test_me
                return arg * 2 

            YetAnother2.do_test_me = wrong_test_me

            yet_another_login_server = locator.get_server(
                coordinator_server_address.address,
                SampleServerType.Login,
                None
            )

            self.assertNotEquals(
                    login_server,
                    yet_another_login_server
                )

            full_name = '%s.%s' % ( yet_another_login_server.__class__.__module__, yet_another_login_server.__class__.__name__ )
            self.assertEquals(
                    'voodoo.gen.protocols.SOAP.ClientSOAP.ClientSOAP',
                    full_name
                )

            answer = yet_another_login_server.method1(msg)
            self.assertEquals(
                    msg * 3,
                    answer
                )

            def wrong_test_me_forever(self,arg):
                return arg * 2 

            YetAnother2.do_test_me = wrong_test_me_forever

            locator.inform_server_not_working(yet_another_login_server,SampleServerType.Login,None)

            return # TODO: 

            # YetAnother2 doesn't work anymore, and the other two ports are not going to work
            self.assertRaises(
                LocatorExceptions.NoServerFoundException,
                locator.get_server,
                coordinator_server_address.address,
                SampleServerType.Login,
                None
            )

        @uses_module(ServerSOAP)
        def test_simple_soap_server(self):
            cfg_manager= ConfigurationManager.ConfigurationManager()
            cfg_manager.append_module(configuration_module)

            map = CoordInfo.CoordinationMap()

            login_t = SampleServerType.Login
            coordinator_t = SampleServerType.Coordinator
            map.add_new_machine ('machine0')
            map.add_new_instance('machine0','instance0')
            map.add_new_server  ('machine0','instance0','server0',coordinator_t,())
            map.add_new_server  ('machine0','instance0','server1',login_t,())

            # 1st: address
            server_ip_address1 = SOAPAddress.Address('127.0.0.1:12349@NETWORK')
            server_ip_address2 = SOAPAddress.Address('127.0.0.1:12350@NETWORK')

            # 2nd: network
            soap_network1 = SOAPNetwork.SOAPNetwork(server_ip_address1)
            soap_network2 = SOAPNetwork.SOAPNetwork(server_ip_address2)

            # 3rd: accesses
            access_soap1 = Access.Access( 
                Protocols.SOAP,AccessLevel.network, ( soap_network1, )
            )
            access_soap2 = Access.Access( 
                Protocols.SOAP,AccessLevel.network, ( soap_network2, )
            )

            # 4th: appending accesses
            map.append_accesses(
                'machine0','instance0','server0',( access_soap1, )
            )
            map.append_accesses(
                'machine0','instance0','server1',( access_soap2, )
            )

            # Generating real servers
            # Coordinator must implement Protocols.Direct too
            # in order to be used by the local locator
            generated_coordinator = ServerSkel.factory(
                    cfg_manager,
                    (Protocols.Direct, Protocols.SOAP), coordinator_methods
                )

            class RealCoordinatorServer(CoordinatorServer.CoordinatorServer,generated_coordinator):
                def __init__(self,cfg_manager, map,*args,**kargs):
                    CoordinatorServer.CoordinatorServer.__init__(self,cfg_manager, map, *args, **kargs)

            coordinator_server_address = DirectAddress.Address(
                        "machine0",
                        "instance0",
                        "server0"
                    )

            s1= RealCoordinatorServer(
                    cfg_manager,
                    map,
                    Direct = (coordinator_server_address.address,), 
                    SOAP = ('',12349)
                )
            s1.start()


            generated_login = ServerSkel.factory(
                    cfg_manager,
                    Protocols.SOAP, login_methods
                )

            class RealLoginServer(generated_login):
                def do_method1(self,arg):
                    return arg * 3

            s2 = RealLoginServer( 
                    SOAP = ('',12350)
                )
            s2.start()
        
            server_type_handler = ServerTypeHandler.ServerTypeHandler(
                    SampleServerType,
                    {
                        'Login' : login_methods,
                        'Coordinator' : coordinator_methods,
                        'YetAnother' : []
                    }
                )

            locator = ServerLocator.ServerLocator(
                    coordinator_server_address,
                    server_type_handler
                )
            login_server = locator.get_server(
                    coordinator_server_address.address,
                    SampleServerType.Login,
                    None
                )

            msg = "test_simple_soap_server"
            answer = login_server.method1(msg)
            self.assertEquals(
                    msg * 3,
                    answer
                )

    else:
        print >> sys.stderr, "Some tests at ServerLocator skipped; SOAPpy not installed"

    def test_system_cache(self):
        locator = self._get_new_locator()

        # There must be no server at the beginning
        self.assertEquals(
                None,
                locator._get_server_from_cache(
                    ServerTypeSample.Login,
                    ()
                )
            )

        locator._save_server_in_cache(
                self._login_server1,
                ServerTypeSample.Login,
                ()
            )

        self.assertEquals(
                self._login_server1,
                locator._get_server_from_cache(
                    ServerTypeSample.Login,
                    ()
                )
            )
        self.assertRaises(
                LocatorExceptions.ServerFoundInCacheException,
                locator._save_server_in_cache,
                self._login_server1,
                ServerTypeSample.Login,
                ()
            )
        # Reset the cache
        self._reset_locator_cache(locator)
        
        # By _save_server_in_registry_and_cache
        locator._save_server_in_registry_and_cache(
                self._login_server1,
                ServerTypeSample.Login,
                (),
                self.login_server1_address
            )
        self.assertEquals(
                self._login_server1,
                locator._get_server_from_cache(
                    ServerTypeSample.Login,
                    ()
                )
            )
        self.assertEquals(
                self._login_server1,
                locator._get_server_from_registry(
                    self.login_server1_address
                )
            )
    
    def test_errors(self):
        locator = self._get_new_locator()
        self.assertRaises(
                LocatorExceptions.NotAServerTypeException,
                locator.get_server,
                "address",
                ":-D",
                ()
            )

        # Checking _retrieve_session_id_from_coordinator
        # and _get_server_from_coordinator

        class Sample:
            def new_query(self, address, server_type,restrictions):
                raise ProtocolExceptions.ProtocolException("lalala")
            def get_server(self,session_id):
                raise ProtocolExceptions.ProtocolException("lalala")

        class Sample2:
            def new_query(self, address, server_type, restrictions):
                raise Exception("lelele")
            def get_server(self,session_id):
                raise Exception("lalala")

        locator._coordinator = Sample()
        self.assertRaises(
            LocatorExceptions.ProblemCommunicatingWithCoordinatorException,
            locator._retrieve_session_id_from_coordinator,
            'address',
            'la',
            'le'
        )
        self.assertRaises(
            LocatorExceptions.ProblemCommunicatingWithCoordinatorException,
            locator._get_server_from_coordinator,
            'la'
        )

        locator._coordinator = Sample2()
        self.assertRaises(
            LocatorExceptions.ProblemCommunicatingWithCoordinatorException,
            locator._retrieve_session_id_from_coordinator,
            'address',
            'la',
            'le'
        )
        self.assertRaises(
            LocatorExceptions.ProblemCommunicatingWithCoordinatorException,
            locator._get_server_from_coordinator,
            'la'
        )

        # Checking _test_server
        class MyServer:
            def test_me(self,arg):
                return arg + arg

        class MyServer2:
            def test_me(self,arg):
                raise Exception("hola")

        class MyServer3:
            def test_me(self,arg):
                raise MyServer3()

        class MyServer4:
            def test_me(self,arg):
                return arg

        class MyAddress:
            def __init__(self):
                self.address = "hola"

        self.assertEquals(
                locator._test_server(MyServer(),MyAddress()),
                False
            )

        self.assertEquals(
                locator._test_server(MyServer2(),MyAddress()),
                False
            )

        #TODO: this should not be commented, but there is a problem
        # with Python 2to3 converter. See voodoo.gen.locator.ServerLocator
        #self.assertEquals(
        #       locator._test_server(MyServer3(),MyAddress()),
        #       False
        #   )

        self.assertEquals(
                locator._test_server(MyServer4(),MyAddress()),
                True
            )

    def test_get_server(self):
        locator = self._get_new_locator()

        # Hooking the coordinatorImplementor do_get_server

        # CoordinatorImplementor says "I don't find any server"
        old_do_get_server = self._coordinatorImplementor.do_get_server
        def do_get_server1(self, session_id):
            raise CoordinatorServerExceptions.NoServerFoundException("No server found for session_id = " + session_id)
        self._coordinatorImplementor.do_get_server = do_get_server1

        # By default, no server is found
        self.assertRaises(
                LocatorExceptions.NoServerFoundException,
                locator.get_server,
                'address',
                ServerTypeSample.Login,
                ()
            )

        # CoordinatorImplementor says "The first time, I find the 
        # login_server1_address; the second time, I don't find any"
        login_server1_address = self.login_server1_address
        global keep_returning_login_server
        keep_returning_login_server = True

        def do_get_server2(self, session_id):
            global keep_returning_login_server
            if keep_returning_login_server:
                keep_returning_login_server = False
                return login_server1_address
            else:
                raise CoordinatorServerExceptions.NoServerFoundException("No server found for session_id = " + session_id)
        self._coordinatorImplementor.do_get_server = do_get_server2

        generated_server = locator.get_server("address",ServerTypeSample.Login,())
        msg = 'hello there'
        self.assertEquals(
                generated_server.method1(msg),
                msg + " through Login Server"
            )

        # Now the locator server should have it in the cache
        # Let's substitute new_query by a function that throws an exception
        # so as to check that it is really never called
        old_do_new_query = self._coordinatorImplementor.do_new_query
        def do_new_query3(self,a,b,c):
            raise ArithmeticError("This should never happen")

        self._coordinatorImplementor.do_new_query = do_new_query3

        tmp_coordinator = self.coordinator_server_address.create_client(
                self.server_type_handler.retrieve_methods(
                    self.server_type_handler.module.Coordinator
                )
            )

        self.assertRaises(
                ArithmeticError,
                tmp_coordinator.new_query,
                'a',
                'b',
                'c'
            )
        # Does the locator retrieve the server from the cache?
        generated_server2 = locator.get_server('address',ServerTypeSample.Login,())
        self.assertEquals(
                generated_server,
                generated_server2
            )
        # Yuhu!
        # Stop hooking new_query
        self._coordinatorImplementor.do_new_query = old_do_new_query

        self._reset_locator_cache(locator)
        # Now it's not in the cache, but it should be in the registry
        self._coordinatorImplementor.do_get_server = do_get_server2
        keep_returning_login_server = True
        generated_server3 = locator.get_server('address',ServerTypeSample.Login,())
        self.assertEquals(
                generated_server,
                generated_server3
            )

        # Now let's try the ServerFoundInCacheException :-)
        def do_get_server4(self, session_id):
            locator._save_server_in_cache(
                    generated_server,
                    ServerTypeSample.Login,
                    ()
                )
            return login_server1_address

        self._coordinatorImplementor.do_get_server = do_get_server4
        
        self._reset_locator_cache(locator)
        generated_server4 = locator.get_server('address',ServerTypeSample.Login,())
        self.assertEquals(
                generated_server,
                generated_server4
            )

        # Stop hooking do_get_server
        keep_returning_login_server = True
        self._coordinatorImplementor.do_get_server = old_do_get_server

    def test_all_get_server(self):
        locator = self._get_new_locator()

        # Hooking the coordinatorImplementor do_get_server

        # CoordinatorImplementor says "I don't find any server"
        old_do_get_server = self._coordinatorImplementor.do_get_server
        def do_get_server1(self, session_id):
            raise CoordinatorServerExceptions.NoServerFoundException("No server found for session_id = " + session_id)
        self._coordinatorImplementor.do_get_server = do_get_server1

        # By default, no server is found
        self.assertRaises(
                LocatorExceptions.NoServerFoundException,
                locator.get_server,
                'address',
                ServerTypeSample.Login,
                ()
            )

        # CoordinatorImplementor says "The first time, I find the 
        # login_server1_address; the second time, I don't find any"
        login_server1_address = self.login_server1_address
        global keep_returning_login_server
        keep_returning_login_server = True

        def do_get_server2(self, session_id):
            global keep_returning_login_server
            if keep_returning_login_server:
                keep_returning_login_server = False
                return login_server1_address
            else:
                raise CoordinatorServerExceptions.NoServerFoundException("No server found for session_id = " + session_id)
        self._coordinatorImplementor.do_get_server = do_get_server2

        generated_server = locator.get_server("address",ServerTypeSample.Login,())
        msg = 'hello there'
        self.assertEquals(
                generated_server.method1(msg),
                msg + " through Login Server"
            )

        # Now the locator server should have it in the cache
        # Let's substitute new_query by a function that throws an exception
        # so as to check that it is really never called
        old_do_new_query = self._coordinatorImplementor.do_new_query
        def do_new_query3(self,a,b,c):
            raise ArithmeticError("This should never happen")

        self._coordinatorImplementor.do_new_query = do_new_query3

        tmp_coordinator = self.coordinator_server_address.create_client(
                self.server_type_handler.retrieve_methods(
                    self.server_type_handler.module.Coordinator
                )
            )

        self.assertRaises(
                ArithmeticError,
                tmp_coordinator.new_query,
                'a',
                'b',
                'c'
            )
        # Does the locator retrieve the server from the cache?
        generated_server2 = locator.get_server('address',ServerTypeSample.Login,())
        self.assertEquals(
                generated_server,
                generated_server2
            )
        # Yuhu!
        # Stop hooking new_query
        self._coordinatorImplementor.do_new_query = old_do_new_query

        self._reset_locator_cache(locator)
        # Now it's not in the cache, but it should be in the registry
        self._coordinatorImplementor.do_get_server = do_get_server2
        keep_returning_login_server = True
        generated_server3 = locator.get_server('address',ServerTypeSample.Login,())
        self.assertEquals(
                generated_server,
                generated_server3
            )

        # Now let's try the ServerFoundInCacheException :-)
        def do_get_server4(self, session_id):
            locator._save_server_in_cache(
                    generated_server,
                    ServerTypeSample.Login,
                    ()
                )
            return login_server1_address

        self._coordinatorImplementor.do_get_server = do_get_server4
        
        self._reset_locator_cache(locator)
        generated_server4 = locator.get_server('address',ServerTypeSample.Login,())
        self.assertEquals(
                generated_server,
                generated_server4
            )

        # Stop hooking do_get_server
        keep_returning_login_server = True
        self._coordinatorImplementor.do_get_server = old_do_get_server

    def test_get_all_servers(self):
        locator = self._get_new_locator()

        # Hooking the coordinatorImplementor do_get_server

        # CoordinatorImplementor says "I don't find any server"
        old_do_get_all_servers = self._coordinatorImplementor.do_get_all_servers
        def do_get_all_servers1(self, original_server_address,server_type, restrictions):
            return []
        self._coordinatorImplementor.do_get_all_servers = do_get_all_servers1

        # By default, no server is found
        self.assertEquals(
                [],
                locator.get_all_servers('address',ServerTypeSample.Login,())
            )

        # Return both servers
        login_server1_address = self.login_server1_address
        login_server2_address = self.login_server2_address
        global keep_returning_login_server
        keep_returning_login_server = True

        class FakeNetwork(object):
            def __init__(self, addr):
                super(FakeNetwork,self).__init__()
                self.address = addr

        obj1, obj2 = 'hello1','hello2'
        def do_get_all_servers2(self, original_server_address, server_type, restrictions):
            return [
                    (
                        # It should be a CoordServer, but...
                        obj1, 
                        (
                            FakeNetwork(
                                login_server1_address
                            ),
                        )
                    ),
                    (
                        # It should be a CoordServer, but...
                        obj2, 
                        (
                            FakeNetwork(
                                login_server2_address
                            ),
                        )
                    )
                ]

        self._coordinatorImplementor.do_get_all_servers = do_get_all_servers2

        generated_servers = locator.get_all_servers("address",ServerTypeSample.Login,())

        self.assertEquals(
                2,
                len(generated_servers)
            )

        generated_server1 = generated_servers[0]
        generated_server2 = generated_servers[1]

        self.assertEquals(
                2,
                len(generated_server1)
            )
        self.assertEquals(
                2,
                len(generated_server2)
            )

        self.assertEquals(
                obj1,
                generated_server1[0]
            )

        self.assertEquals(
                obj2,
                generated_server2[0]
            )

        self.assertEquals(
                1,
                len(generated_server1[1])
            )
    
        self.assertEquals(
                1,
                len(generated_server2[1])
            )
    
        generated_server1_client = generated_server1[1][0]
        generated_server2_client = generated_server2[1][0]

        msg = 'hello there'
        self.assertEquals(
                generated_server1_client.method1(msg),
                msg + " through Login Server"
            )

        self.assertEquals(
                generated_server2_client.method1(msg),
                msg + " through Login Server"
            )

        # Stop hooking do_get_all_servers
        keep_returning_login_server = True
        self._coordinatorImplementor.do_get_all_servers = old_do_get_all_servers

    def test_get_server_from_coord_address(self):
        locator = self._get_new_locator()

        # Hooking the coordinatorImplementor do_get_server

        # CoordinatorImplementor says "I don't find any network"
        old_do_get_networks = self._coordinatorImplementor.do_get_networks
        def do_get_networks1(self, original_server_address, server_address):
            return []
        self._coordinatorImplementor.do_get_networks = do_get_networks1

        # If no network is available, LocatorExceptions.NoNetworkAvailableException is raised
        self.assertRaises(
                LocatorExceptions.NoNetworkAvailableException,
                locator.get_server_from_coord_address,
                self.coordinator_server_address,
                self.login_server1_address,
                ServerTypeSample.Login
        )

        login_server1_address = self.login_server1_address
        def do_get_networks2(self, original_server_address, server_address):
            return [
                    DirectNetwork.DirectNetwork(login_server1_address)
            ]
        self._coordinatorImplementor.do_get_networks = do_get_networks2

        server_instances = locator.get_server_from_coord_address(
                self.coordinator_server_address,
                self.login_server1_address,
                ServerTypeSample.Login
            )

        server_instance = server_instances[0]

        random_msg = str(random.random())
        self.assertEquals(
                random_msg + " through Login Server",
                server_instance.method1(random_msg)
            )
        
        self._coordinatorImplementor.do_get_networks = old_do_get_networks

def suite():
    return unittest.makeSuite(ServerLocatorTestCase)

if __name__ == '__main__':
    unittest.main()

