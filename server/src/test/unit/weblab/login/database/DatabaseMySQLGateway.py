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

import test.unit.configuration as configuration

import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.data.UserType as UserType

import weblab.login.database.DatabaseGateway as DatabaseGateway
import weblab.database.DatabaseAccountManager as DAM
import weblab.login.database.dao.UserAuth as UserAuth

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

from weblab.database.DatabaseConstants import AUTH
from weblab.database.DatabaseConstants import READ, NAME

class DatabaseMySQLGatewayTestCase(unittest.TestCase):
    def setUp(self):
        auth_user = DAM.DatabaseUserInformation( 'wl_auth_read', 'wl_auth_read_password' )
        self.auth_credentials = { NAME : AUTH, READ : auth_user }

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)

        self.auth_gateway = DatabaseGateway.create_auth_gateway(cfg_manager)

    def test_user_password(self):
        #This user doesn't exist
        self.assertRaises(
                DbExceptions.DbUserNotFoundException,
                self.auth_gateway.check_user_password,
                self.auth_credentials,
                'user',
                'password'
            )

        #This user exists, but the password is wrong
        self.assertRaises(
                DbExceptions.DbNoUserAuthNorPasswordFoundException,
                self.auth_gateway.check_user_password,
                self.auth_credentials,
                'admin1',
                'wrong_password'
            )

        #This user exists and the password is correct
        user_type, user_id, user_auths = self.auth_gateway.check_user_password(
                    self.auth_credentials,
                    'admin1',
                    'password'
                )
        self.assertEquals(
            UserType.administrator,
            user_type
        )
        self.assertEquals(
            1,
            user_id
        )
        self.assertEquals(
            None,
            user_auths
        )

    def test_user_password_invalid_hash_algorithm(self):
        self.assertRaises(
            DbExceptions.DbHashAlgorithmNotFoundException,
            self.auth_gateway.check_user_password,
            self.auth_credentials,
            'student7',
            'password'
        )

    def test_user_password_invalid_password_format(self):
        self.assertRaises(
            DbExceptions.DbInvalidPasswordFormatException,
            self.auth_gateway.check_user_password,
            self.auth_credentials,
            'student8',
            'password'
        )
        
    def test_user_password_ldap(self):
        user_type, user_id, user_auths = self.auth_gateway.check_user_password(
                self.auth_credentials,
                'studentLDAP1',
                None
            )
        self.assertEquals(
            UserType.student,
            user_type
        )
        self.assertEquals(
            1,
            len(user_auths)
        )
        self.assertTrue(
            isinstance(user_auths[0], UserAuth.LdapUserAuth)
        )
        self.assertEquals(
            'cdk.deusto.es',
            user_auths[0].domain
        )
        self.assertEquals(
            'ldaps://castor.cdk.deusto.es',
            user_auths[0].ldap_uri
        )
    
    def test_user_password_user_auth_without_user_auth(self):
        self.assertRaises(
            DbExceptions.DbNoUserAuthNorPasswordFoundException,
            self.auth_gateway.check_user_password,
            self.auth_credentials,
            'studentLDAPwithoutUserAuth',
            None
        )

def suite():
    return unittest.makeSuite(DatabaseMySQLGatewayTestCase)

if __name__ == '__main__':
    unittest.main()

