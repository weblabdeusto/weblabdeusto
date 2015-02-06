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
import signal
import time
import tempfile
import unittest
import threading

from weblab.admin.script import weblab as weblab_admin
from test.util.ports import new as new_port

class ServerLoader(threading.Thread):
    def __init__(self, weblab_dir):
        super(ServerLoader, self).__init__()
        self.weblab_dir = weblab_dir
        self.exc_info = None

    def __enter__(self):
        self.start()
        raw_input("Started...")

    def run(self):
        try:
            sys.argv = shlex.split("weblab-admin start %s" % self.weblab_dir)
            weblab_admin()
        except:
            self.exc_info = sys.exc_info()
            print self.exc_info

    def __exit__(self, *args, **kwargs):
        current_pid = os.getpid()
        os.kill(current_pid, signal.SIGTERM)
        self.join()

class ScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_folder = tempfile.mkdtemp(prefix = 'remove_me_', suffix = '_testcase_script')
        self.weblab_dir = os.path.join(self.temporary_folder, 'weblab')
        self.argv = list(sys.argv)

    def tearDown(self):
        # TODO: Look for child processes and kill them any way with a kill. For example, in voodoo.process_starter we could create a _CHILD_PROCESSES variable and a method such as kill_children()
        # which will kill those processes created and update the list
        sys.argv = self.argv
        shutil.rmtree(self.temporary_folder)

    @unittest.skip("weblab-admin create still requires the user to run raw_input() since in voodoo.launcher in the __main__ there's a raw_input")
    def test_simple(self):
        start_port = new_port() + 1000
        # Make a port space
        for _ in xrange(10):
            new_port()
        port = new_port()
        sys.argv = shlex.split("weblab-admin create %s --quiet --not-interactive --socket-wait=%s --start-port=%s" % (self.weblab_dir, port, start_port))
        weblab_admin()
        loader = ServerLoader(self.weblab_dir)
        with loader:
            print "Test the service, which is running in other thread"

        print loader.exc_info

def suite():
    return unittest.makeSuite(ScriptTestCase)

if __name__ == '__main__':
    unittest.main()
