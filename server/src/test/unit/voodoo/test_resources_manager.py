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
from __future__ import print_function, unicode_literals

import unittest
import voodoo.resources_manager as RM

class ResourceManagerTest(unittest.TestCase):
    def test_is_testing(self):
        # We are testing
        self.assertTrue(RM.is_testing())

def suite():
    return unittest.makeSuite(ResourceManagerTest)

if __name__ == '__main__':
    unittest.main()

