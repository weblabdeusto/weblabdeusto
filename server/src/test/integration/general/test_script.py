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

import os
import sys
import shlex
import shutil
import tempfile
import unittest

from weblab.admin.script import weblab as weblab_admin

class ScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_folder = tempfile.mkdtemp(prefix = 'remove_me_', suffix = '_testcase_script')
        self.weblab_dir = os.path.join(self.temporary_folder, 'weblab')
        self.argv = list(sys.argv)

    def tearDown(self):
        sys.argv = self.argv
        shutil.rmtree(self.temporary_folder)

    def test_running(self):
        sys.argv = shlex.split("weblab-admin create %s --quiet" % self.weblab_dir)
        weblab_admin()
        sys.argv = shlex.split("weblab-admin start %s" % self.weblab_dir)
        try:
            weblab_admin()
            print "TEST THE SERVICES"
        finally:
            sys.argv = shlex.split("weblab-admin stop %s" % self.weblab_dir)
            weblab_admin()

def suite():
    return unittest.makeSuite(ScriptTestCase)

if __name__ == '__main__':
    unittest.main()
