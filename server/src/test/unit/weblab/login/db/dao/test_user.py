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

import unittest

import weblab.login.db.dao.user as UserAuth
import weblab.db.exc as DbErrors

class DbUserAuthTestCase(unittest.TestCase):
    def test_create_user_failed(self):
        self.assertRaises(
            DbErrors.DbUnsupportedUserAuth,
            UserAuth.UserAuth.create_user_auth,
            'whatever that does not exist',
            'the configuration'
        )

    def test_invalid_ldap_configuration(self):
        self.assertRaises(
            DbErrors.DbInvalidUserAuthConfigurationError,
            UserAuth.UserAuth.create_user_auth,
            UserAuth.LdapUserAuth.NAME,
            'the configuration'
        )

    def test_create_user_auth_right(self):
        ldap_uri = 'ldaps://castor.cdk.deusto.es'
        domain   = 'cdk.deusto.es'
        base     = 'dc=cdk,dc=deusto,dc=es'
        ldap_user_auth = UserAuth.UserAuth.create_user_auth(
                UserAuth.LdapUserAuth.NAME,
                'ldap_uri=' + ldap_uri + ';domain=' + domain + ';base=' + base
            )
        self.assertTrue(
                isinstance(
                    ldap_user_auth,
                    UserAuth.LdapUserAuth
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
        ldap_user_auth = UserAuth.UserAuth.create_user_auth(
                UserAuth.LdapUserAuth.NAME,
                'ldap_uri=' + ldap_uri + ';domain=' + domain + ';base=' + base
            )
        self.assertTrue(
                isinstance(
                    ldap_user_auth,
                    UserAuth.LdapUserAuth
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

        tia_user_auth = UserAuth.UserAuth.create_user_auth(
                UserAuth.TrustedIpAddressesUserAuth.NAME,
                single_ip
            )
        self.assertTrue(
                isinstance(
                    tia_user_auth,
                    UserAuth.TrustedIpAddressesUserAuth
                )
            )
        self.assertEquals(
                ('20.0.0.5',),
                tuple(tia_user_auth.addresses)
            )

        two_ips   = '20.0.0.5, 20.0.0.6'
        tia_user_auth = UserAuth.UserAuth.create_user_auth(
                UserAuth.TrustedIpAddressesUserAuth.NAME,
                two_ips
            )
        self.assertTrue(
                isinstance(
                    tia_user_auth,
                    UserAuth.TrustedIpAddressesUserAuth
                )
            )
        self.assertEquals(
                ('20.0.0.5','20.0.0.6'),
                tuple(tia_user_auth.addresses)
            )

def suite():
    return unittest.makeSuite(DbUserAuthTestCase)

if __name__ == '__main__':
    unittest.main()

