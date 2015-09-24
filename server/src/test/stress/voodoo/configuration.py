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

import unittest

import test.util.stress as stress_util

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

class ConfigurationManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        def func():
            self.cfg_manager.get_value("db_driver")

        self.runner = stress_util.MainRunner(func, "ConfigurationManager")

    def test_sequential(self):
        iterations = 10000
        max_time   = 0.3
        print "seq",max(self.runner.run_sequential(iterations, max_time))

    def test_concurrent(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con",max(self.runner.run_threaded(threads, iterations, max_time))

def suite():
    return unittest.makeSuite(ConfigurationManagerTestCase)

if __name__ == '__main__':
    unittest.main()

