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
import pmock

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

def create_ldap_object(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception):
    valid_user_plus_domain = valid_user + '@cdk.deusto.es'
    ldap_object = pmock.Mock()
    ldap_object.expects(
            pmock.once()
        ).simple_bind_s(
            pmock.eq(valid_user_plus_domain),
            pmock.eq(valid_passwd)
        ).will(
        pmock.return_value(
            None
        )
    )
    ldap_object.expects(
            pmock.once()
        ).simple_bind_s(
            pmock.eq(valid_user_plus_domain),
            pmock.eq(invalid_passwd)
        ).will(
        pmock.raise_exception(
            ldap.INVALID_CREDENTIALS("Invalid user/password")
        )
    )
    ldap_object.expects(
            pmock.once()
        ).simple_bind_s(
            pmock.eq(valid_user_plus_domain),   
            pmock.eq(passwd_that_will_raise_exception)
        ).will(
        pmock.raise_exception(
            Exception("generic exception")
        )
    )
    ldap_object.expects(
            pmock.once()
        ).unbind_s()
    return ldap_object

def create_ldap_module(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception, uri_that_will_fail):
    ldap_object = create_ldap_object(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception)

    ldap_module = pmock.Mock()
    ldap_module.expects(
            pmock.once()
        ).initialize(
            pmock.eq('ldaps://castor.cdk.deusto.es')
        ).will(
            pmock.return_value(
                ldap_object
            )
        )
    ldap_module.expects(
            pmock.once()
        ).initialize(
            pmock.eq(uri_that_will_fail)
        ).will(
            pmock.raise_exception(
                Exception("fail")
            )
        )
    return ldap_module



class LoginAuthTestCase(unittest.TestCase):
    if LoginAuth.LDAP_AVAILABLE:
        def _create_user_auth(self):
            return UserAuth.UserAuth.create_user_auth(
                    UserAuth.LdapUserAuth.NAME,
                    'domain=cdk.deusto.es;ldap_uri=ldaps://castor.cdk.deusto.es'
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
            ldap_module = create_ldap_module(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception, uri_that_will_fail)

            LoginAuth._ldap_provider.ldap_module = ldap_module

            self.assertTrue(
                login_auth.authenticate(valid_user, valid_passwd)
            )

        def test_ldap_login_auth_invalid(self):
            user_auth = self._create_user_auth()
            login_auth = LoginAuth.LoginAuth.create(user_auth)
            ldap_module = create_ldap_module(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception, uri_that_will_fail)

            LoginAuth._ldap_provider.ldap_module = ldap_module

            self.assertFalse(
                login_auth.authenticate(valid_user, invalid_passwd)
            )

        def test_ldap_login_auth_general_exception_binding(self):
            user_auth = self._create_user_auth()
            login_auth = LoginAuth.LoginAuth.create(user_auth)
            ldap_module = create_ldap_module(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception, uri_that_will_fail)

            LoginAuth._ldap_provider.ldap_module = ldap_module

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
            ldap_module = create_ldap_module(valid_user, valid_passwd, invalid_passwd, passwd_that_will_raise_exception, uri_that_will_fail)

            LoginAuth._ldap_provider.ldap_module = ldap_module

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

