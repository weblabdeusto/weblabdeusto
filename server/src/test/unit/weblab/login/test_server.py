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
from __future__ import print_function, unicode_literals

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

from voodoo.gen import CoordAddress
import voodoo.configuration      as ConfigurationManager

import weblab.core.login.manager as login_manager
from weblab.core.server import UserProcessingServer
import weblab.core.server as core_api
import weblab.core.login.simple.ldap_auth as ldap_auth
import weblab.core.login.exc as LoginErrors

import test.unit.configuration as configuration_module
from test.util.wlcontext import wlcontext

fake_wrong_user           = "fake_wrong_user"
fake_wrong_passwd         = "fake_wrong_passwd"

fake_right_user           = "student1"
fake_right_passwd         = "password"

fake_ldap_user            = "studentLDAP1"
fake_ldap_passwd          = "password"
fake_ldap_invalid_passwd  = "fake_ldap_invalid_passwd"

class LoginServerTestCase(unittest.TestCase):

    def setUp(self):
        coord_address = CoordAddress.translate(
                "server0:instance0@machine0")

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.core_server = UserProcessingServer(coord_address, None, self.cfg_manager)

    def tearDown(self):
        self.core_server.stop()

    def test_invalid_user_and_invalid_password(self):
        login_manager.LOGIN_FAILED_DELAY = 0.2
        with wlcontext(self.core_server):
            self.assertRaises(
                LoginErrors.InvalidCredentialsError,
                core_api.login,
                fake_wrong_user,
                fake_wrong_passwd
            )

    def test_valid_user_and_invalid_password(self):
        login_manager.LOGIN_FAILED_DELAY = 0.2
        with wlcontext(self.core_server):
            self.assertRaises(
                LoginErrors.InvalidCredentialsError,
                core_api.login,
                fake_right_user,
                fake_wrong_passwd
            )

    @unittest.skipIf(not LDAP_AVAILABLE, "LDAP module not available")
    def test_ldap_user_right(self):
        mockr = mocker.Mocker()
        ldap_auth._ldap_provider.ldap_module = mockr.mock()
        with wlcontext(self.core_server):
            session_id = core_api.login(fake_ldap_user, fake_ldap_passwd)

        self.assertTrue( isinstance(session_id, SessionId) )
        self.assertTrue( len(session_id.id) > 5 )

    @unittest.skipIf(not LDAP_AVAILABLE, "LDAP module not available")
    def test_ldap_user_invalid(self):
        mockr = mocker.Mocker()
        ldap_object = mockr.mock()
        ldap_object.simple_bind_s(fake_ldap_user + '@cdk.deusto.es', fake_ldap_invalid_passwd)
        mockr.throw(ldap.INVALID_CREDENTIALS)
        ldap_module = mockr.mock()
        ldap_module.initialize('ldaps://castor.cdk.deusto.es')
        mockr.result(ldap_object)
        ldap_auth._ldap_provider.ldap_module = ldap_module

        with wlcontext(self.core_server):
            with mockr:
                self.assertRaises(
                    LoginErrors.InvalidCredentialsError,
                    core_api.login,
                    fake_ldap_user,
                    fake_ldap_invalid_passwd
                )

    def test_login_delay(self):
        login_manager.LOGIN_FAILED_DELAY = 0.2
        #Sometimes it's 0.999323129654
        #0.001 should be ok, but just in case
        ERROR_MARGIN = 0.01
        start_time = time.time()
        with wlcontext(self.core_server):
            self.assertRaises(
                    LoginErrors.InvalidCredentialsError,
                    core_api.login,
                    fake_wrong_user,
                    fake_wrong_passwd
                )
        finish_time = time.time()
        self.assertTrue((finish_time + ERROR_MARGIN - start_time) >= login_manager.LOGIN_FAILED_DELAY)

    def test_right_session(self):
        with wlcontext(self.core_server):
            session_id = core_api.login(fake_right_user, fake_right_passwd)
            self.assertTrue( isinstance(session_id, SessionId) )
            self.assertTrue( len(session_id.id) > 5 )

def suite():
    return unittest.makeSuite(LoginServerTestCase)

if __name__ == '__main__':
    unittest.main()

