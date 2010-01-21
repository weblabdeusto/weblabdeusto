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

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

class DatabaseAccountManagerTestCase(unittest.TestCase):
    def setUp(self):
        import weblab.database.DatabaseAccountManager as DAM
        self.DAM = DAM
    def test_credentials(self):
        self.assertRaises(
                DbExceptions.DbCredentialsLevelNotFoundException,
                self.DAM.get_credentials,
                'hola'
            )
        
def suite():
    return unittest.makeSuite(DatabaseAccountManagerTestCase)

if __name__ == '__main__':
    unittest.main()

