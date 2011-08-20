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

from __future__ import with_statement

import sys
import unittest
import mocker
import time

try:
    import ldap
except ImportError:
    LDAP_AVAILABLE = False
else:
    LDAP_AVAILABLE = True
    
import weblab.data.ServerType as ServerType

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions
import voodoo.gen.exceptions.locator.LocatorExceptions as LocatorExceptions
import voodoo.gen.locator.EasyLocator as EasyLocator
import voodoo.configuration.ConfigurationManager      as ConfigurationManager

import weblab.methods as weblab_methods

import weblab.login.LoginServer as LoginServer
import weblab.login.LoginAuth as LoginAuth
import weblab.login.exc as LoginExceptions

import test.unit.configuration as configuration_module

fake_wrong_user           = "fake_wrong_user"
fake_wrong_passwd         = "fake_wrong_passwd"

fake_right_user           = "student1"
fake_right_passwd         = "password"

fake_ldap_user            = "studentLDAP1"
fake_ldap_passwd          = "password"
fake_ldap_invalid_passwd  = "fake_ldap_invalid_passwd"

fake_ups_session_id       = "lalala"

class FakeUPServer(object):
    def __init__(self):
        super(FakeUPServer,self).__init__()

    def reserve_session(self, db_session_id):
        return fake_ups_session_id, "server_route"

class FakeLocator(object):
    def __init__(self):
        super(FakeLocator,self).__init__()
        self.fake_ups_server = FakeUPServer()
        self.servers_not_working = []

    def get_server(self, coord_address, server_type, restrictions):
        if server_type == ServerType.UserProcessing:
            return self.fake_ups_server

    def retrieve_methods(self, server_type):
        if server_type == ServerType.UserProcessing:
            return weblab_methods.UserProcessing
        elif server_type == ServerType.Database:
            return weblab_methods.Database

    def inform_server_not_working(self, server, server_type, restrictions):
        self.servers_not_working.append(server)

def get_no_server(self, coord_address, server_type, restrictions):
    raise LocatorExceptions.NoServerFoundException("lol")

def broken_login_user(self, username, password):
    raise ProtocolExceptions.RemoteException("p0wn3d","p0wn3d")

def broken_reserve_session(self, db_session_id):
    raise ProtocolExceptions.RemoteException("p0wn3d","p0wn3d")

class LoginServerTestCase(unittest.TestCase):
    
    def setUp(self):
        coord_address = CoordAddress.CoordAddress.translate_address(
                "server0:instance0@machine0"
            )

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.real_locator = FakeLocator()
        self.locator      = EasyLocator.EasyLocator(
                coord_address,
                self.real_locator
            )

        self.login_server = LoginServer.LoginServer(
                    coord_address,
                    self.locator,
                    self.cfg_manager
                )

    def tearDown(self):
        self.login_server.stop()

    def test_invalid_user_and_invalid_password(self):
        LoginServer.LOGIN_FAILED_DELAY = 0.2
        self.assertRaises(
            LoginExceptions.InvalidCredentialsException,
            self.login_server.login,
            fake_wrong_user,
            fake_wrong_passwd
        )

    def test_valid_user_and_invalid_password(self):
        LoginServer.LOGIN_FAILED_DELAY = 0.2
        self.assertRaises(
            LoginExceptions.InvalidCredentialsException,
            self.login_server.login,
            fake_right_user,
            fake_wrong_passwd
        )
        
    if LDAP_AVAILABLE:
        def test_ldap_user_right(self):
            mockr = mocker.Mocker()
            LoginAuth._ldap_provider.ldap_module = mockr.mock()
            session_id = self.login_server.login(fake_ldap_user, fake_ldap_passwd)
            
            self.assertEquals(
                fake_ups_session_id,
                session_id
            )

        def test_ldap_user_invalid(self):
            mockr = mocker.Mocker()
            ldap_object = mockr.mock()
            ldap_object.simple_bind_s(fake_ldap_user + '@cdk.deusto.es', fake_ldap_invalid_passwd)
            mockr.throw(ldap.INVALID_CREDENTIALS)
            ldap_module = mockr.mock()
            ldap_module.initialize('ldaps://castor.cdk.deusto.es')
            mockr.result(ldap_object)
            LoginAuth._ldap_provider.ldap_module = ldap_module 

            with mockr:
                self.assertRaises(
                    LoginExceptions.InvalidCredentialsException,
                    self.login_server.login,
                    fake_ldap_user, 
                    fake_ldap_invalid_passwd
                )

    else:
        print >> sys.stderr, "Two tests skipped in LoginServer since ldap is not available"

    def test_login_delay(self):
        LoginServer.LOGIN_FAILED_DELAY = 0.2
        #Sometimes it's 0.999323129654
        #0.001 should be ok, but just in case
        ERROR_MARGIN = 0.01
        start_time = time.time()
        self.assertRaises(
                LoginExceptions.InvalidCredentialsException,
                self.login_server.login,
                fake_wrong_user,
                fake_wrong_passwd
            )
        finish_time = time.time()
        self.assertTrue((finish_time + ERROR_MARGIN - start_time) >= LoginServer.LOGIN_FAILED_DELAY)

    def test_right_session(self):
        session_id = self.login_server.login(
                    fake_right_user,
                    fake_right_passwd
                )
        self.assertEquals(
                fake_ups_session_id,
                session_id
            )

    def test_login_failed_exception_reserving(self):
        old_reserve_session = FakeUPServer.reserve_session
        FakeUPServer.reserve_session = broken_reserve_session
        try:
            self.assertRaises(
                LocatorExceptions.UnableToCompleteOperationException,
                self.login_server.login,
                fake_right_user,
                fake_right_passwd
            )
        finally:
            FakeUPServer.reserve_session = old_reserve_session

        self.assertEquals(
            1,
            len(self.real_locator.servers_not_working)
        )
        self.assertEquals(
            self.real_locator.fake_ups_server,
            self.real_locator.servers_not_working[0]
        )

    def test_no_server_found_retrieving(self):
        old_get_server = FakeLocator.get_server
        FakeLocator.get_server = get_no_server
        
        try:
            self.assertRaises(
                LocatorExceptions.UnableToCompleteOperationException,
                self.login_server.login,
                fake_right_user,
                fake_right_passwd
            )
        finally:
            FakeLocator.get_server = old_get_server

def suite():
    return unittest.makeSuite(LoginServerTestCase)

if __name__ == '__main__':
    unittest.main()

