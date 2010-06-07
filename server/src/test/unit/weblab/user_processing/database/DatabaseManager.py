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
import weblab.user_processing.database.DatabaseManager as DatabaseManager
import weblab.database.DatabaseSession as DatabaseSession

class DatabaseServerTestCase(unittest.TestCase):
    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.dm = DatabaseManager.UserProcessingDatabaseManager(cfg_manager)
        
    def test_get_available_experiments(self):
        session_id = DatabaseSession.ValidDatabaseSessionId("student2", "student")
        experiments = self.dm.get_available_experiments(session_id)
        self.assertTrue(
                len(experiments) >= 3
            )

        experiment_names =list( ( experiment.experiment.name for experiment in experiments ))

        self.assertTrue( 'ud-fpga' in experiment_names )
        self.assertTrue( 'ud-pld' in experiment_names )
        self.assertTrue( 'ud-gpib' in experiment_names )
        
    def test_retrieve_user_information(self):
        session_id = DatabaseSession.ValidDatabaseSessionId("admin1", "administrator")
        user = self.dm.retrieve_user_information(session_id)

        self.assertNotEquals(user, None)
        self.assertEquals(user.role.name, "administrator")
        self.assertEquals("admin1",user.login)
        self.assertEquals("Name of administrator 1",user.full_name)
        self.assertEquals("weblab@deusto.es",user.email)
        
    def test_get_groups(self):
        session_id = DatabaseSession.ValidDatabaseSessionId("student2", "student")
        groups = self.dm.get_groups(session_id)
        self.assertTrue( len(groups) == 1 )

        groups_names =list( ( group.name for group in groups ))

        self.assertTrue( '5A' in groups_names )
        
    def test_get_experiments(self):
        session_id = DatabaseSession.ValidDatabaseSessionId("student2", "student")
        experiments = self.dm.get_experiments(session_id)
        self.assertTrue( len(experiments) >= 3 )

        experiments_names =list( ( experiment.name for experiment in experiments ))

        self.assertTrue( 'ud-fpga' in experiments_names )
        self.assertTrue( 'ud-pld' in experiments_names )
        self.assertTrue( 'ud-gpib' in experiments_names )


def suite():
    return unittest.makeSuite(DatabaseServerTestCase)

if __name__ == '__main__':
    unittest.main()

