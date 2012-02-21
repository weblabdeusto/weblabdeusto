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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import unittest

from test.util.module_disposer import uses_module
import voodoo.gen.protocols.InternetSocket.ServerInternetSocket as ServerInternetSocket
import voodoo.gen.protocols.InternetSocket.ClientInternetSocket as ClientInternetSocket

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import time

PORT = 12142

class TestServer(object):
    def __init__(self):
        super(TestServer, self).__init__()
    def do_method0(self):
        return "This is the result of method0()"
    def do_method1(self, arg1):
        return "This is the result of method1() (arg1=%s)" % arg1
    def do_method2(self, arg1, arg2):
        return "This is the result of method2() (arg1=%s and arg2=%s)" % ( arg1, arg2 )
    def do_test_me(self, arg):
        return arg

class InternetSocketTestCase(unittest.TestCase):

    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

    def _test_server_generate_with_parameter(self, methods):
        klz = ServerInternetSocket.generate(self.cfg_manager, methods)
        for method_name in methods:
            self.assertTrue( hasattr(klz, method_name), "generate() was intended to generate a class with the method %s" % method_name)
            self.assertNotEquals(getattr(klz, method_name).__doc__.find(method_name), -1, "%s() has not its name in its docstring" % method_name)
        self.assertTrue( hasattr(klz, "test_me"), "generate() was intended to generate a class with the method test_me()")
        return klz

    @uses_module(ServerInternetSocket)
    def test_server_generate_with_a_tuple(self):
        methods = ("method0", "method1", "method2")
        self._test_server_generate_with_parameter(methods)

    @uses_module(ServerInternetSocket)
    def test_server_generate_with_a_list(self):
        methods = ["method0", "method1", "method2"]
        self._test_server_generate_with_parameter(methods)

    @uses_module(ServerInternetSocket)
    def test_server_generate_with_a_dict(self):
        methods = {"method0": "foo"*100, "method1": "bar"*100, "method2": "foobar"*100}
        klz = self._test_server_generate_with_parameter(methods)
        self.assertNotEquals(klz.method0.__doc__.find("foo"*100), -1, "method0() has not its documentation in its docstring")
        self.assertNotEquals(klz.method1.__doc__.find("bar"*100), -1, "method1() has not its documentation in its docstring")
        self.assertNotEquals(klz.method2.__doc__.find("foobar"*100), -1, "method2() has not its documentation in its docstring")

    def _test_client_generate_with_parameter(self, methods):
        klz = ClientInternetSocket.generate(methods)
        for method_name in methods:
            self.assertTrue( hasattr(klz, method_name), "generate() was intended to generate a class with the method %s" % method_name)
            self.assertNotEquals(getattr(klz, method_name).__doc__.find(method_name), -1, "%s() has not its name in its docstring" % method_name)
        self.assertTrue( hasattr(klz, "test_me"), "generate() was intended to generate a class with the method test_me()")
        return klz

    def test_client_generate_with_a_tuple(self):
        methods = ("method0", "method1", "method2")
        self._test_client_generate_with_parameter(methods)

    def test_client_generate_with_a_list(self):
        methods = ["method0", "method1", "method2"]
        self._test_client_generate_with_parameter(methods)

    def test_client_generate_with_a_dict(self):
        methods = {"method0": "foo"*100, "method1": "bar"*100, "method2": "foobar"*100}
        klz = self._test_server_generate_with_parameter(methods)
        self.assertNotEquals(klz.method0.__doc__.find("foo"*100), -1, "method0() has not its documentation in its docstring")
        self.assertNotEquals(klz.method1.__doc__.find("bar"*100), -1, "method1() has not its documentation in its docstring")
        self.assertNotEquals(klz.method2.__doc__.find("foobar"*100), -1, "method2() has not its documentation in its docstring")

    @uses_module(ServerInternetSocket)
    def test_server_on_off(self):
        methods = ["method0", "method1", "method2"]
        klz = ServerInternetSocket.generate(self.cfg_manager, methods)
        internet_socket_server = klz("127.0.0.1", PORT + 1)
        parent = TestServer()
        internet_socket_server.register_parent(parent)
        internet_socket_server.start(False)
        time.sleep(0.1)
        internet_socket_server.stop()

    @uses_module(ServerInternetSocket)
    def test_server_on_request_off(self):
        methods = ["method0", "method1", "method2"]
        klz_server = ServerInternetSocket.generate(self.cfg_manager, methods)
        server = klz_server("127.0.0.1", PORT + 2)
        parent = TestServer()
        server.register_parent(parent)
        server.start(False)
        klz_client = ClientInternetSocket.generate(methods)
        client = klz_client("127.0.0.1", PORT + 2)
        result = client.method0()
        self.assertEquals(result, "This is the result of method0()")
        result = client.method1("foobar")
        self.assertEquals(result, "This is the result of method1() (arg1=foobar)")
        result = client.method2("foo", "bar")
        self.assertEquals(result, "This is the result of method2() (arg1=foo and arg2=bar)")
        server.stop()

def suite():
    return unittest.makeSuite(InternetSocketTestCase)

if __name__ == '__main__':
    unittest.main()
