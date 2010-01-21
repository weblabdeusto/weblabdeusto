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

import mocker

import voodoo.gen.locator.EasyLocator as EasyLocator
import voodoo.gen.coordinator.CoordAddress as CoordAddress

import test.unit.voodoo.gen.locator.ServerTypeSample as ServerTypeSample

class MyLoginServer(object):
    def __init__(self):
        self.calls = []
    def login(self, username, password):
        self.calls.append((username,password))

class EasyLocatorTestCase(unittest.TestCase):
    def setUp(self):
        self.locator_mocker = mocker.Mocker()
        self.locator        = self.locator_mocker.mock()
        self.coord_addr     = CoordAddress.CoordAddress('server:instance@machine')
        self.coord_addr2    = CoordAddress.CoordAddress('server2:instance@machine')

        self.easy_locator   = EasyLocator.EasyLocator(
                self.coord_addr,
                self.locator
            )
        
    def test_get_server(self):
        self.locator.get_server(
                self.coord_addr.address,
                ServerTypeSample.Login,
                ('hey','ho')
            )
        result = 'a server'
        self.locator_mocker.result(result)
        self.locator_mocker.replay()

        returned_result = self.easy_locator.get_server(
                ServerTypeSample.Login,
                ('hey','ho')
            )

        self.assertEquals(result, returned_result)

        self.locator_mocker.verify()

    def test_get_server_default(self):
        self.locator.get_server(
                self.coord_addr.address,
                ServerTypeSample.Login,
                ()
            )
        result = 'a server'
        self.locator_mocker.result(result)
        self.locator_mocker.replay()

        returned_result = self.easy_locator.get_server(
                ServerTypeSample.Login
            )

        self.assertEquals(result, returned_result)

        self.locator_mocker.verify()

    def test_get_server_from_coordaddr(self):
        self.locator.retrieve_methods(
                ServerTypeSample.Login
            )
        self.locator_mocker.result(['login'])
        self.locator.get_server_from_coord_address(
                self.coord_addr,
                self.coord_addr2,
                ServerTypeSample.Login,
                5
            )
        
        result = MyLoginServer()
        self.locator_mocker.result([result])
        self.locator_mocker.replay()

        returned_result = self.easy_locator.get_server_from_coordaddr(
                self.coord_addr2,
                ServerTypeSample.Login,
                5
            )

        returned_result.login('haha','hehe')

        self.locator_mocker.verify()

        self.assertEquals(
                1,
                len(result.calls)
            )

        self.assertEquals(
                ('haha','hehe'),
                result.calls[0]
            )

    def test_get_server_from_coordaddr_default(self):
        self.locator.retrieve_methods(
                ServerTypeSample.Login
            )
        self.locator_mocker.result(['login'])
        self.locator.get_server_from_coord_address(
                self.coord_addr,
                self.coord_addr2,
                ServerTypeSample.Login,
                'all'
            )

        result = MyLoginServer()
        self.locator_mocker.result([result])
        self.locator_mocker.replay()

        returned_result = self.easy_locator.get_server_from_coordaddr(
                self.coord_addr2,
                ServerTypeSample.Login
            )

        results = returned_result.login('haha','hehe')

        self.locator_mocker.verify()

        self.assertEquals(
                1,
                len(result.calls)
            )

        self.assertEquals(
                ('haha','hehe'),
                result.calls[0]
            )


def suite():
    return unittest.makeSuite(EasyLocatorTestCase)

if __name__ == '__main__':
    unittest.main()


