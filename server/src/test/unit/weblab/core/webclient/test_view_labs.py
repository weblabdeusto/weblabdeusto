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
from __future__ import print_function
import unittest

from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY


class TestViewLabs(unittest.TestCase):

    def setUp(self):
        GLOBAL_REGISTRY.clear()
        """
        Prepares the test by creating a new weblab instance from a for-testing configuration.
        The instance is configured *not* to start a flask server, but to allow Flask test methods
        instead.
        :return:
        """

        # Load the configuration of the weblab instance that we have set up for just this test.
        self.global_config = load_dir('test/deployments/webclient_dummy')

        # Start the weblab instance. Because we have activated the dont-start flag it won't actually
        # start listening on the port, but let us use the Flask test methods instead.
        self.handler = self.global_config.load_process('myhost', 'myprocess')

        self.core_server = GLOBAL_REGISTRY['mycore:myprocess@myhost']

        self.app = self.core_server.app.test_client()
        """ :type: flask.testing.FlaskClient """

        # Login.
        rv = self.app.post('weblab/login', data=dict(username='any', password='password'))
        self.assertEqual(rv.status_code, 302, "Login POST for any / password does not return 302")

    def test_nothing(self):
        pass

    def test_labs_page(self):
        """
        Ensure that the labs page seems to load.
        """
        rv = self.app.get('/weblab/')
        self.assertEqual(rv.status_code, 200, "Labs page does not return 200")
        self.assertIn("My Experiments", rv.data, "Labs page does not contain the expected 'My Experiments' text")
        self.assertIn("Name of any", rv.data, "Labs page does not contain the expected 'Name of any' text")
        self.assertIn("Log out", rv.data, "Labs page does not contain the expected 'Log out' text")
        # self.assertIn("Filter by", rv.data, "Labs page does not contain the expected 'Filter by' text")

    def tearDown(self):
        """
        Shutdown the WebLab instance that we have started for the test.
        """
        rv = self.app.post('/weblab/login', data=dict(username='any', password='password'))
        self.assertEqual(rv.status_code, 302, "Login POST with right pass does not return 302")

        self.handler.stop()


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(TestViewLabs),
        ))

