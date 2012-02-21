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

import test.unit.configuration as configuration

import voodoo.configuration as ConfigurationManager
import weblab.core.db.manager as DatabaseManager

class DatabaseServerTestCase(unittest.TestCase):
    """Note: Methods tested from UserProcessingServer won't be tested again here."""

    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.dm = DatabaseManager.UserProcessingDatabaseManager(cfg_manager)


def suite():
    return unittest.makeSuite(DatabaseServerTestCase)

if __name__ == '__main__':
    unittest.main()

