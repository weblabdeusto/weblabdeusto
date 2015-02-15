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
import time

from test.util.script import ServerCreator

from weblab.data.experiments import ExperimentId

class ScriptTestCase(unittest.TestCase):
    def test_simple(self):
        with ServerCreator(u"--cores=1") as sc:
            client = sc.create_client()
            session_id = client.login(u'admin', u'password')
            self.assertNotEquals(session_id, None)

    def test_multiple_cores(self):
        with ServerCreator(u"--cores=3 --db-engine=mysql --db-name=WebLabIntTests1 --db-user=weblab --db-passwd=weblab --coordination-engine=redis") as sc:
            clients = []
            session_ids = []
            reservation_ids = []
            for n in range(20):
                client = sc.create_client()
                session_id = client.login(u'admin', u'password')
                self.assertNotEquals(session_id, None)
                clients.append(client)
                session_ids.append(session_id)
                status = client.reserve_experiment(session_id, ExperimentId("dummy", "Dummy experiments"), "{}", "{}")
            time.sleep(0.5)
                


def suite():
    return unittest.makeSuite(ScriptTestCase)

if __name__ == '__main__':
    unittest.main()
