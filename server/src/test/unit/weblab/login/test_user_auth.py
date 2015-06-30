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

import unittest

import sys
import mocker

try:
    import ldap
except ImportError:
    pass

from test.util.optional_modules import OptionalModuleTestCase
import weblab.core.login.exc as LoginErrors
import weblab.core.login.simple as auth_simple
import weblab.core.login.simple.ldap_auth as ldap_auth
from weblab.core.login.simple import create_user_auth
from weblab.core.exc import DbUnsupportedUserAuth, DbInvalidUserAuthConfigurationError

class DbUserAuthTestCase(unittest.TestCase):
    def test_create_user_failed(self):
        self.assertRaises(
            DbUnsupportedUserAuth,
            create_user_auth,
            'whatever that does not exist',
            'the configuration',
            None
        )

    def test_invalid_ldap_configuration(self):
        self.assertRaises(
            DbInvalidUserAuthConfigurationError,
            create_user_auth,
            auth_simple.LdapUserAuth.NAME,
            'the configuration',
            None
        )

    def test_create_user_auth_right(self):
        ldap_uri = 'ldaps://castor.cdk.deusto.es'
        domain   = 'cdk.deusto.es'
        base     = 'dc=cdk,dc=deusto,dc=es'
        ldap_user_auth = create_user_auth(
                auth_simple.LdapUserAuth.NAME,
                'ldap_uri=' + ldap_uri + ';domain=' + domain + ';base=' + base,
                None
            )
        self.assertTrue(
                isinstance(
                    ldap_user_auth,
                    auth_simple.LdapUserAuth
                )
            )
        self.assertEquals(
                ldap_uri,
                ldap_user_auth.ldap_uri
            )
        self.assertEquals(
                domain,
                ldap_user_auth.domain
            )
        self.assertEquals(
                base,
                ldap_user_auth.base
            )
        ldap_uri = 'ldaps://castor-4.cdk_4.deusto.es/'
        domain   = 'cdk_4-3.deusto.es'
        base     = 'dc=cdk,dc=de_us-to,dc=es'
        ldap_user_auth = create_user_auth(
                auth_simple.LdapUserAuth.NAME,
                'ldap_uri=' + ldap_uri + ';domain=' + domain + ';base=' + base,
                None
            )
        self.assertTrue(
                isinstance(
                    ldap_user_auth,
                    auth_simple.LdapUserAuth
                )
            )
        self.assertEquals(
                ldap_uri,
                ldap_user_auth.ldap_uri
            )
        self.assertEquals(
                domain,
                ldap_user_auth.domain
            )
        self.assertEquals(
                base,
                ldap_user_auth.base
            )

    def test_create_trusted_addresses_user_auth_right(self):
        single_ip = '20.0.0.5'

        tia_user_auth = create_user_auth(
                auth_simple.TrustedIpAddressesUserAuth.NAME,
                single_ip, None
            )
        self.assertTrue(
                isinstance(
                    tia_user_auth,
                    auth_simple.TrustedIpAddressesUserAuth
                )
            )
        self.assertEquals(
                ('20.0.0.5',),
                tuple(tia_user_auth.addresses)
            )

        two_ips   = '20.0.0.5, 20.0.0.6'
        tia_user_auth = create_user_auth(
                auth_simple.TrustedIpAddressesUserAuth.NAME,
                two_ips, None
            )
        self.assertTrue(
                isinstance(
                    tia_user_auth,
                    auth_simple.TrustedIpAddressesUserAuth
                )
            )
        self.assertEquals(
                ('20.0.0.5','20.0.0.6'),
                tuple(tia_user_auth.addresses)
            )

valid_user                       = 'valid_user'
valid_passwd                     = 'valid_passwd'
invalid_passwd                   = 'invalid_passwd'
passwd_that_will_raise_exception = 'passwd_that_will_raise_exception'
uri_that_will_fail               = 'uri that will fail'

class LoginAuthTestCase(mocker.MockerTestCase):

    def _create_user_auth(self):
        return create_user_auth(
                auth_simple.LdapUserAuth.NAME,
                'ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es',
                None,
            )

    @unittest.skipIf(not ldap_auth.LDAP_AVAILABLE, "LDAP module not available")
    def test_ldap_login_auth_valid(self):
        user_auth = self._create_user_auth()
        ldap_object = self.mocker.mock()
        ldap_object.simple_bind_s(valid_user + '@cdk.deusto.es', valid_passwd)
        self.mocker.result(None)
        ldap_module = self.mocker.mock()
        ldap_module.initialize('ldaps://castor.cdk.deusto.es')
        self.mocker.result(ldap_object)
        ldap_object.unbind_s()
        ldap_auth._ldap_provider.ldap_module = ldap_module

        self.mocker.replay()
        self.assertTrue(
            user_auth.authenticate(valid_user, valid_passwd)
        )

    @unittest.skipIf(not ldap_auth.LDAP_AVAILABLE, "LDAP module not available")
    def test_ldap_login_auth_invalid(self):
        user_auth = self._create_user_auth()

        ldap_object = self.mocker.mock()
        ldap_object.simple_bind_s(valid_user + '@cdk.deusto.es', invalid_passwd)
        self.mocker.throw(ldap.INVALID_CREDENTIALS("Invalid user/password"))
        ldap_module = self.mocker.mock()
        ldap_module.initialize('ldaps://castor.cdk.deusto.es')
        self.mocker.result(ldap_object)
        ldap_auth._ldap_provider.ldap_module = ldap_module

        self.mocker.replay()
        self.assertFalse(
            user_auth.authenticate(valid_user, invalid_passwd)
        )

    @unittest.skipIf(not ldap_auth.LDAP_AVAILABLE, "LDAP module not available")
    def test_ldap_login_auth_general_exception_binding(self):
        user_auth = self._create_user_auth()

        ldap_object = self.mocker.mock()
        ldap_object.simple_bind_s(valid_user + '@cdk.deusto.es', passwd_that_will_raise_exception)
        self.mocker.throw(Exception("generic exception"))
        ldap_module = self.mocker.mock()
        ldap_module.initialize('ldaps://castor.cdk.deusto.es')
        self.mocker.result(ldap_object)
        ldap_auth._ldap_provider.ldap_module = ldap_module

        self.mocker.replay()
        self.assertRaises(
            LoginErrors.LdapBindingError,
            user_auth.authenticate,
            valid_user,
            passwd_that_will_raise_exception
        )

    @unittest.skipIf(not ldap_auth.LDAP_AVAILABLE, "LDAP module not available")
    def test_ldap_login_auth_general_exception_initializing(self):
        user_auth = self._create_user_auth()
        user_auth.ldap_uri = uri_that_will_fail

        ldap_module = self.mocker.mock()
        ldap_module.initialize(uri_that_will_fail)
        self.mocker.throw(Exception("fail"))
        ldap_auth._ldap_provider.ldap_module = ldap_module

        self.mocker.replay()
        self.assertRaises(
            LoginErrors.LdapInitializingError,
            user_auth.authenticate,
            valid_user,
            valid_passwd
        )


class LdapNotAvailableTestCase(OptionalModuleTestCase):

    MODULE    = ldap_auth
    ATTR_NAME = 'LDAP_AVAILABLE'

    def test_ldap_not_available(self):
        def func():
            user_auth = create_user_auth(
                    auth_simple.LdapUserAuth.NAME,
                    'ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es',
                    None,
                )
            user_auth.authenticate("foo","bar")
        self._test_func_without_module(func)

def suite():
    return unittest.TestSuite((
                unittest.makeSuite(DbUserAuthTestCase),
                unittest.makeSuite(LoginAuthTestCase),
                unittest.makeSuite(LdapNotAvailableTestCase),
            ))

if __name__ == '__main__':
    unittest.main()

