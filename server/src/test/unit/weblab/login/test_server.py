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

from voodoo.sessions.session_id import SessionId
import weblab.data.server_type as ServerType

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.protocols.ProtocolErrors as ProtocolErrors
import voodoo.configuration      as ConfigurationManager

import weblab.methods as weblab_methods

import weblab.core.login as login_manager
from weblab.core.server import UserProcessingServer
import weblab.login.simple.ldap_auth as ldap_auth
import weblab.login.exc as LoginErrors

import test.unit.configuration as configuration_module

fake_wrong_user           = "fake_wrong_user"
fake_wrong_passwd         = "fake_wrong_passwd"

fake_right_user           = "student1"
fake_right_passwd         = "password"

fake_ldap_user            = "studentLDAP1"
fake_ldap_passwd          = "password"
fake_ldap_invalid_passwd  = "fake_ldap_invalid_passwd"

class LoginServerTestCase(unittest.TestCase):

    def setUp(self):
        coord_address = CoordAddress.CoordAddress.translate_address(
                "server0:instance0@machine0")

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.login_server = UserProcessingServer(coord_address, None, self.cfg_manager)

    def tearDown(self):
        self.login_server.stop()

    def test_invalid_user_and_invalid_password(self):
        login_manager.LOGIN_FAILED_DELAY = 0.2
        self.assertRaises(
            LoginErrors.InvalidCredentialsError,
            self.login_server.do_login,
            fake_wrong_user,
            fake_wrong_passwd
        )

    def test_valid_user_and_invalid_password(self):
        login_manager.LOGIN_FAILED_DELAY = 0.2
        self.assertRaises(
            LoginErrors.InvalidCredentialsError,
            self.login_server.do_login,
            fake_right_user,
            fake_wrong_passwd
        )

    if LDAP_AVAILABLE:
        def test_ldap_user_right(self):
            mockr = mocker.Mocker()
            ldap_auth._ldap_provider.ldap_module = mockr.mock()
            session_id = self.login_server.do_login(fake_ldap_user, fake_ldap_passwd)

            self.assertTrue( isinstance(session_id, SessionId) )
            self.assertTrue( len(session_id.id) > 5 )

        def test_ldap_user_invalid(self):
            mockr = mocker.Mocker()
            ldap_object = mockr.mock()
            ldap_object.simple_bind_s(fake_ldap_user + '@cdk.deusto.es', fake_ldap_invalid_passwd)
            mockr.throw(ldap.INVALID_CREDENTIALS)
            ldap_module = mockr.mock()
            ldap_module.initialize('ldaps://castor.cdk.deusto.es')
            mockr.result(ldap_object)
            ldap_auth._ldap_provider.ldap_module = ldap_module

            with mockr:
                self.assertRaises(
                    LoginErrors.InvalidCredentialsError,
                    self.login_server.do_login,
                    fake_ldap_user,
                    fake_ldap_invalid_passwd
                )

    else:
        print >> sys.stderr, "Two tests skipped in LoginServer since ldap is not available"

    def test_login_delay(self):
        login_manager.LOGIN_FAILED_DELAY = 0.2
        #Sometimes it's 0.999323129654
        #0.001 should be ok, but just in case
        ERROR_MARGIN = 0.01
        start_time = time.time()
        self.assertRaises(
                LoginErrors.InvalidCredentialsError,
                self.login_server.do_login,
                fake_wrong_user,
                fake_wrong_passwd
            )
        finish_time = time.time()
        self.assertTrue((finish_time + ERROR_MARGIN - start_time) >= login_manager.LOGIN_FAILED_DELAY)

    def test_right_session(self):
        session_id = self.login_server.do_login(
                    fake_right_user,
                    fake_right_passwd
                )
        self.assertTrue( isinstance(session_id, SessionId) )
        self.assertTrue( len(session_id.id) > 5 )

def suite():
    return unittest.makeSuite(LoginServerTestCase)

if __name__ == '__main__':
    unittest.main()

