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

from test.util.ModuleDisposer import uses_module
import voodoo.gen.protocols.SOAP.ServerSOAP as ServerSOAP

import voodoo.gen.generators as gens
import voodoo.gen.protocols.Protocols as Protocols

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

methods1 = {'method1':'this method returns something like "method1"'}
methods2 = {'method2':'this method returns something like "method2"'}
methods = (methods1,methods2)

SENTENCE1='Hello'
SENTENCE2='Goodbye'
sentences = (SENTENCE1, SENTENCE2)

PORT = 8094

def get_server(protocol,methods,sentence):
    cfg_manager= ConfigurationManager.ConfigurationManager()
    cfg_manager.append_module(configuration_module)

    def do_method(self,whatever):
        return sentence + whatever
    class Server(gens.ServerSkel.factory(cfg_manager, protocol,methods)):
        pass
    for i in methods:
        setattr(Server,'do_'+i,do_method)
    return Server

def get_client(protocol,methods):
    return gens.ClientSkel.factory(protocol,methods)

server_name = 'sample_server_name'

class GeneratorsTestCase(unittest.TestCase):
    def test_direct(self):
        for m in methods:
            for sentence in sentences:
                server = get_server(
                        Protocols.Direct,
                        m,
                        sentence
                    )(Direct = (server_name,))
                server.start()
                client = get_client(
                        Protocols.Direct,
                        m
                    )(server)
                for i in m:
                    method = getattr(client,i)
                    rand_value = str(random.random())
                    result = method(rand_value)
                    self.assertEquals(
                            result,
                            sentence + rand_value
                        )
                rand_value = str(random.random())
                self.assertEquals(
                    client.test_me(rand_value),
                    rand_value
                )
                server.stop()
   
    if ServerSOAP.SOAPPY_AVAILABLE:
        @uses_module(ServerSOAP)
        def test_soap(self):
            for m in methods:
                for sentence in sentences:
                    server = get_server( Protocols.SOAP, m, sentence)(SOAP = ('',PORT))
                    server.start()
                    client = get_client( Protocols.SOAP, m)('localhost',PORT)
                    for i in m:
                        method = getattr(client,i)
                        rand_value = str(random.random())
                        result = method(rand_value)
                        self.assertEquals( result, sentence + rand_value )
                    rand_value = str(random.random())
                    self.assertEquals(
                        client.test_me(rand_value),
                        rand_value
                    )
                    server.stop()

        @uses_module(ServerSOAP)
        def test_two_protocols(self):
            for m in methods:
                for sentence in sentences:
                    server = get_server(
                            (
                                Protocols.SOAP,
                                Protocols.Direct
                            ),
                            m,
                            sentence
                        )(
                            SOAP = ('',PORT),
                            Direct = (server_name,)
                        )
                    server.start()
                    client1 = get_client(
                            Protocols.SOAP,
                            m
                        )('localhost',PORT)
                    client2 = get_client(
                            Protocols.Direct,
                            m
                        )(server)
                    for i in m:
                        for client in client1,client2:
                            method = getattr(client,i)
                            rand_value = str(random.random())
                            result = method(rand_value)
                            self.assertEquals(
                                    result,
                                    sentence + rand_value
                                )
                    server.stop()
                    
        @uses_module(ServerSOAP)
        def test_two_soap_in_one_port(self):
            for sentence in sentences:
                server1 = get_server(
                        Protocols.SOAP,
                        methods1,
                        sentence
                    )(SOAP = ('',PORT))
                server2 = get_server(
                        Protocols.SOAP,
                        methods2,
                        sentence
                    )(SOAP = ('',PORT))
                server1.start()
                server2.start()
                
                client1 = get_client(
                        Protocols.SOAP,
                        methods1
                    )('localhost',PORT)
                client2 = get_client(
                        Protocols.SOAP,
                        methods2
                    )('localhost',PORT)
                
                for i in methods1:
                    method = getattr(client1,i)
                    rand_value = str(random.random())
                    result = method(rand_value)
                    self.assertEquals(
                            result,
                            sentence + rand_value
                        )
                    
                for i in methods2:
                    method = getattr(client2,i)
                    rand_value = str(random.random())
                    result = method(rand_value)
                    self.assertEquals(
                            result,
                            sentence + rand_value
                        )
                server1.stop()
                server2.stop()
    else:
        print >> sys.stderr, "Some tests at GeneratorsTestCase skipped; SOAPpy not installed"
            
        
def suite():
    return unittest.makeSuite(GeneratorsTestCase)

if __name__ == '__main__':
    unittest.main()

