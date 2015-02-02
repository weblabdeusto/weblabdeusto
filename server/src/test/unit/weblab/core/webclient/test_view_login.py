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
# Author: Luis Rodriguez-Gil <luis.rodriguezgil@deusto.es>
#         Pablo Orduña <pablo.orduna@deusto.es>
#
import unittest
from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY

class TestViewLogin(unittest.TestCase):

    def setUp(self):

        # Load the configuration of the weblab instance that we have set up for just this test.
        self.global_config = load_dir('test/deployments/webclient_dummy')

        # Start the weblab instance. Because we have activated the dont-start flag it won't actually
        # start listening on the port, but let us use the Flask test methods instead.
        self.handler = self.global_config.load_process('myhost', 'myprocess')

        self.core_server = GLOBAL_REGISTRY['mycore:myprocess@myhost']
        self.app = self.core_server.app.test_client()

    def test_client(self):
        rv = self.app.get('/weblab/login/web/login/?username=any&password=password')
        print rv.data

    def tearDown(self):
        self.handler.stop()

