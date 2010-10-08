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
import mocker

try:
    import ldap
except ImportError:
    pass

from test.util.optional_modules import OptionalModuleTestCase
import weblab.login.LoginAuth as LoginAuth
import weblab.login.database.dao.UserAuth as UserAuth
import weblab.exceptions.login.LoginExceptions as LoginExceptions

valid_user                       = 'valid_user'
valid_passwd                     = 'valid_passwd'
invalid_passwd                   = 'invalid_passwd'
passwd_that_will_raise_exception = 'passwd_that_will_raise_exception'
uri_that_will_fail               = 'uri that will fail'

class LoginAuthTestCase(mocker.MockerTestCase):
    
    if LoginAuth.LDAP_AVAILABLE:

        def _create_user_auth(self):
            return UserAuth.UserAuth.create_user_auth(
                    UserAuth.LdapUserAuth.NAME,
                    'ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es'
                )

        def test_create(self):
            user_auth = self._create_user_auth()
            login_auth = LoginAuth.LoginAuth.create(user_auth)
            self.assertTrue(
                isinstance(
                    login_auth,
                    LoginAuth.LdapLoginAuth
                )
            )

        def test_create_fail(self):
            class SomethingThatHasAName(object):
                pass
            something_with_a_name = SomethingThatHasAName()
            something_with_a_name.name = "something that does not exist"
            self.assertRaises(
                LoginExceptions.LoginUserAuthNotImplementedException,
                LoginAuth.LoginAuth.create,
                something_with_a_name
            )

        def test_ldap_login_auth_valid(self):
            user_auth = self._create_user_auth()
            login_auth = LoginAuth.LoginAuth.create(user_auth)

            ldap_object = self.mocker.mock()
            ldap_object.simple_bind_s(valid_user + '@cdk.deusto.es', valid_passwd)
            self.mocker.result(None)
            ldap_module = self.mocker.mock()
            ldap_module.initialize('ldaps://castor.cdk.deusto.es')
            self.mocker.result(ldap_object)
            ldap_object.unbind_s()
            LoginAuth._ldap_provider.ldap_module = ldap_module
            
            self.mocker.replay()
            self.assertTrue(
                login_auth.authenticate(valid_user, valid_passwd)
            )

        def test_ldap_login_auth_invalid(self):
            user_auth = self._create_user_auth()
            login_auth = LoginAuth.LoginAuth.create(user_auth)

            ldap_object = self.mocker.mock()
            ldap_object.simple_bind_s(valid_user + '@cdk.deusto.es', invalid_passwd)
            self.mocker.throw(ldap.INVALID_CREDENTIALS("Invalid user/password"))
            ldap_module = self.mocker.mock()
            ldap_module.initialize('ldaps://castor.cdk.deusto.es')
            self.mocker.result(ldap_object)
            LoginAuth._ldap_provider.ldap_module = ldap_module
            
            self.mocker.replay()
            self.assertFalse(
                login_auth.authenticate(valid_user, invalid_passwd)
            )

        def test_ldap_login_auth_general_exception_binding(self):
            user_auth = self._create_user_auth()
            login_auth = LoginAuth.LoginAuth.create(user_auth)

            ldap_object = self.mocker.mock()
            ldap_object.simple_bind_s(valid_user + '@cdk.deusto.es', passwd_that_will_raise_exception)
            self.mocker.throw(Exception("generic exception"))
            ldap_module = self.mocker.mock()
            ldap_module.initialize('ldaps://castor.cdk.deusto.es')
            self.mocker.result(ldap_object)
            LoginAuth._ldap_provider.ldap_module = ldap_module

            self.mocker.replay()
            self.assertRaises(
                LoginExceptions.LdapBindingException,
                login_auth.authenticate,
                valid_user, 
                passwd_that_will_raise_exception
            )
        
        def test_ldap_login_auth_general_exception_initializing(self):
            user_auth = self._create_user_auth()
            user_auth.ldap_uri = uri_that_will_fail
            login_auth = LoginAuth.LoginAuth.create(user_auth)
            
            ldap_module = self.mocker.mock()
            ldap_module.initialize(uri_that_will_fail)
            self.mocker.throw(Exception("fail"))
            LoginAuth._ldap_provider.ldap_module = ldap_module

            self.mocker.replay()
            self.assertRaises(
                LoginExceptions.LdapInitializingException,
                login_auth.authenticate,
                valid_user, 
                valid_passwd
            )
    
    else:
        print >> sys.stderr, "LoginAuth tests skipped since ldap module is not available"


class LdapNotAvailableTestCase(OptionalModuleTestCase):
    
    MODULE    = LoginAuth
    ATTR_NAME = 'LDAP_AVAILABLE'

    def test_ldap_not_available(self):
        def func():
            login_auth = LoginAuth.LdapLoginAuth("foo")
            login_auth.authenticate("foo","bar")

        self._test_func_without_module(func)


def suite():
    return unittest.TestSuite((
                unittest.makeSuite(LoginAuthTestCase),
                unittest.makeSuite(LdapNotAvailableTestCase)
            ))

if __name__ == '__main__':
    unittest.main()

