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
from flask import request
from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY

class TestViewLogin(unittest.TestCase):

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

    def test_login_page(self):
        """
        Ensure that the login screen seems to load.
        """
        rv = self.app.get('/weblab/web/webclient/login')
        self.assertEqual(rv.status_code, 200, "Login page does not return 200")
        self.assertIn("Remote Laboratory", rv.data, "Login page does not contain the expected 'Remote Laboratory' text")
        self.assertIn("Support", rv.data, "Login page does not contain the expected 'Support' text")

    def test_login_wrongpass(self):
        """
        Ensure that a login POST with a wrong password results in an 'Invalid username or password' message.
        """
        rv = self.app.post('/weblab/web/webclient/login', data=dict(username='any', password='wrongpassword'))
        """ :type: flask.wrappers.Response """

        self.assertEqual(rv.status_code, 302, "Login POST with wrong pass does not return 302")
        self.assertTrue(rv.location.endswith("/web/webclient/login"), "Redirection does not lead to index")

        rv = self.app.get(rv.location)
        self.assertIn("Invalid username or password", rv.data, "After wrong password login 'Invalid username...' does not appear")

    def test_login_rightpass(self):
        """
        Ensure that a login POST with a right password results in a redirection to the labs page.
        """
        rv = self.app.post('/weblab/web/webclient/login', data=dict(username='any', password='password'))
        """ :type: flask.wrappers.Response """

        self.assertEqual(rv.status_code, 302, "Login POST with right pass does not return 302")
        self.assertTrue(rv.location.endswith("/web/webclient/"), "Redirection does not lead to the labs page")

        with self.app as c:
            # Just so the context is set, to be able to read cookies.
            c.get("/")
            self.assertIn("weblabsessionid", request.cookies, "Cookie weblabsessionid was not set")
            self.assertIn("loginweblabsessionid", request.cookies, "Cookie loginweblabsessionid was not set")


    def tearDown(self):
        """
        Shutdown the WebLab instance that we have started for the test.
        """
        rv = self.app.post('/weblab/web/webclient/login', data=dict(username='any', password='password'))
        self.assertEqual(rv.status_code, 302, "Login POST with right pass does not return 302")

        self.handler.stop()


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(TestViewLogin),
        ))

