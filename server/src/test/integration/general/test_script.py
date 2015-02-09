#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 onwards University of Deusto
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

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient

from test.util.script import ServerCreator

class ScriptTestCase(unittest.TestCase):
    def test_simple(self):
        with ServerCreator("--cores=1") as sc:
            client = WebLabDeustoClient(sc.address)
            session_id = client.login('admin', 'password')
            self.assertNotEquals(session_id, None)

def suite():
    return unittest.makeSuite(ScriptTestCase)

if __name__ == '__main__':
    unittest.main()
