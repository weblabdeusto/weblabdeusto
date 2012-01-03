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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import unittest

import test.unit.configuration as configuration

import voodoo.configuration as ConfigurationManager

import weblab.login.db.gateway as DatabaseGateway
import weblab.login.db.dao.user as UserAuth

import weblab.db.exc as DbExceptions


class DatabaseGatewayTestCase(unittest.TestCase):
    
    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.auth_gateway = DatabaseGateway.AuthDatabaseGateway(cfg_manager)

    def test_user_password(self):
        #This user doesn't exist
        self.assertRaises(
                DbExceptions.DbUserNotFoundException,
                self.auth_gateway.check_user_password,
                'user',
                'password'
            )

        #This user exists, but the password is wrong
        self.assertRaises(
                DbExceptions.DbInvalidUserOrPasswordException,
                self.auth_gateway.check_user_password,
                'admin1',
                'wrong_password'
            )

        #This user exists and the password is correct
        role, user_id, user_auths = self.auth_gateway.check_user_password(
                    'admin1',
                    'password'
                )
        self.assertEquals(
            "administrator",
            role.name
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
            'student7',
            'password'
        )

    def test_user_password_invalid_password_format(self):
        self.assertRaises(
            DbExceptions.DbInvalidPasswordFormatException,
            self.auth_gateway.check_user_password,
            'student8',
            'password'
        )
        
    def test_user_password_ldap(self):
        role, user_id, user_auths = self.auth_gateway.check_user_password(
                'studentLDAP1',
                None
            )
        self.assertEquals(
            "student",
            role.name
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
            'studentLDAPwithoutUserAuth',
            None
        )
        

def suite():
    return unittest.makeSuite(DatabaseGatewayTestCase)

if __name__ == '__main__':
    unittest.main()

