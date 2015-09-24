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

import sys
import StringIO
import unittest

class OptionalModuleTestCase(unittest.TestCase):
    MODULE    = None
    ATTR_NAME = None

    def setUp(self):
        self._backup_available = getattr(self.MODULE, self.ATTR_NAME)
        setattr(self.MODULE, self.ATTR_NAME, False)

    def tearDown(self):
        setattr(self.MODULE, self.ATTR_NAME, self._backup_available)

    def _test_func_without_module(self, func):
        stderr = sys.stderr
        sys.stderr = StringIO.StringIO()
        try:
            func()
            self.assertTrue( len(sys.stderr.getvalue()) > 10 ) # Something has been written
        finally:
            sys.stderr = stderr

