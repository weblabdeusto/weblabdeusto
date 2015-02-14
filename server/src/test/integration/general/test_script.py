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

from test.util.script import ServerCreator

class ScriptTestCase(unittest.TestCase):
    def test_simple(self):
        with ServerCreator(u"--cores=1") as sc:
            client = sc.create_client()
            session_id = client.login(u'admin', u'password')
            self.assertNotEquals(session_id, None)

    def test_multiple_cores(self):
        with ServerCreator(u"--cores=3 --db-engine=mysql --db-name=WebLabIntTests1 --db-user=weblab --db-passwd=weblab --coordination-engine=redis") as sc:
            client = sc.create_client()
            session_id = client.login(u'admin', u'password')
            self.assertNotEquals(session_id, None)

def suite():
    return unittest.makeSuite(ScriptTestCase)

if __name__ == '__main__':
    unittest.main()
