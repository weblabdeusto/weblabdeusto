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

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

class ResourcesCheckerTestCase(unittest.TestCase):
    def test_check_laboratory(self):
        pass # TODO

def suite():
    return unittest.makeSuite(ResourcesCheckerTestCase)

if __name__ == '__main__':
    unittest.main()

