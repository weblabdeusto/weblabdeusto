#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
from __future__ import print_function, unicode_literals

import os
import unittest

import test.util.stress as stress_util

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import voodoo.sessions.manager as SessionManager
import voodoo.sessions.session_type    as SessionType

class SessionManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.session_manager = SessionManager.SessionManager(
                                    self.cfg_manager,
                                    SessionType.Memory,
                                    "foo"
                                )

        def func():
            self.session_manager.create_session()

        self.runner = stress_util.MainRunner(func, "SessionManager")

    def test_print_results(self):
        threads = []
        for i in xrange(1,5):
            threads.append(i)
        for i in xrange(5,101,5):
            threads.append(i)

        iterations = []
        for i in xrange(1,10001,500):
            iterations.append(i)

        print "Generating... SessionManager"
        print "  threaded..."
        if not os.path.exists('logs'):
            os.mkdir('logs')
        self.runner.print_graphics_threaded  ('logs/results_session_manager_threaded.png', threads, 50, 3)
        print "  sequential..."
        self.runner.print_graphics_sequential('logs/results_session_manager_sequential.png', iterations, 3)


def suite():
    return unittest.makeSuite(SessionManagerTestCase)

if __name__ == '__main__':
    unittest.main()

