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
import weblab.login.db.manager as DatabaseManager
import weblab.db.session as DatabaseSession

class DatabaseServerTestCase(unittest.TestCase):
    def setUp(self):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.dm = DatabaseManager.LoginDatabaseManager(cfg_manager)
        
    def test_login_user(self):
        session_id = self.dm.check_credentials('admin1','password')
        self.assertTrue(
                isinstance(
                    session_id,
                    DatabaseSession.ValidDatabaseSessionId
                )
            )


    def test_login_user_ldap(self):
        session_id = self.dm.check_credentials('studentLDAP1',None)
        self.assertTrue(
                isinstance(
                    session_id,
                    DatabaseSession.NotAuthenticatedSessionId
                )
            )
        self.assertEquals(
                'cdk.deusto.es',
                session_id.user_auths[0].domain
            )

def suite():
    return unittest.makeSuite(DatabaseServerTestCase)

if __name__ == '__main__':
    unittest.main()

