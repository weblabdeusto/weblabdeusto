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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import unittest

import test.unit.configuration as configuration

import voodoo.configuration as ConfigurationManager

import weblab.core.db as DatabaseGateway

from weblab.core.exc import DbUserNotFoundError


class DatabaseGatewayTestCase(unittest.TestCase):

    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.auth_gateway = DatabaseGateway.DatabaseGateway(cfg_manager)

    def test_retrieve_role_and_user_auths(self):
        # With user "admin": password 'password', role administrator
        login, role, user_auths = self.auth_gateway.retrieve_role_and_user_auths('admin1')
        self.assertEquals('admin1', login)
        self.assertEquals('administrator', role)
        self.assertEquals(1, len(user_auths))
        self.assertEquals('aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474', user_auths[0].hashed_password)

        # With student: same password, role student
        login, role, user_auths = self.auth_gateway.retrieve_role_and_user_auths('student1')
        self.assertEquals('student1', login)
        self.assertEquals('student', role)
        self.assertEquals(1, len(user_auths))
        self.assertEquals('aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474', user_auths[0].hashed_password)


    def test_retrieve_role_and_user_auths_error(self):
        self.assertRaises(DbUserNotFoundError, self.auth_gateway.retrieve_role_and_user_auths, 'not_exists')

def suite():
    return unittest.makeSuite(DatabaseGatewayTestCase)

if __name__ == '__main__':
    unittest.main()

