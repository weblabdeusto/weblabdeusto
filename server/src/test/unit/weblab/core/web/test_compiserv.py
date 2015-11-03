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
#
from __future__ import print_function
import json
import unittest
import mock
import requests

from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY

from mock import patch


class TestCompiserv(unittest.TestCase):

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

    def test_intro_page_loads(self):
        """
        Ensure that the compiserv index page loads.
        """
        rv = self.app.get('/weblab/web/compiserv/')
        self.assertEqual(rv.status_code, 200, "Compiserv index page does not return 200")

    def _mocked_post(url, data):
        """
        Moc
        """
        resp = requests.Response()
        respobj = {"GeneratedDate": "27/11/2015", "ID": 20, "TokenID": "abcdef"}
        resp._content = json.dumps(respobj)
        return resp

    @mock.patch('weblab.core.web.compiserv.requests.post', mock.Mock(side_effect=_mocked_post))
    def test_lab_page(self):
        """
        Ensure that POST'ing a new compilation job seems to work as expected.
        """
        rv = self.app.post('/weblab/web/compiserv/queue/armc', data='cprogramsource')

        self.assertEqual(rv.status_code, 200, "Lab page does not return 200")

        response = json.loads(rv.data)

        self.assertIn("result", response, "The response to the job POST request does not seem to contain a result key")
        self.assertEqual(response["result"], "accepted", "Result is not 'accepted'")

        self.assertIn("uid", response, "The response to the job POST request does not seem to contain an uid key")
        self.assertEqual(response["uid"], "20+abcdef", "UID is not 20+abcdef as was expected")

    def tearDown(self):
        """
        Shutdown the WebLab instance that we have started for the test.
        """
        rv = self.app.post('/weblab/login', data=dict(username='any', password='password'))
        self.assertEqual(rv.status_code, 302, "Login POST with right pass does not return 302")

        self.handler.stop()


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(TestCompiserv),
        ))