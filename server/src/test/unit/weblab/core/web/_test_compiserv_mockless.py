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


class TestCompiservMockless(unittest.TestCase):

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

    def test_post_compiserv_job(self):
        """
        Ensure that POST'ing a new compilation job seems to work as expected.
        Mocks the remote compilation server.
        """
        rv = self.app.post('/weblab/web/compiserv/queue/armc', data='#include <MKL25Z4.h>\nint main(void) {return 0;}')

        self.assertEqual(rv.status_code, 200, "Lab page does not return 200")

        response = json.loads(rv.data)

        self.assertIn("result", response, "The response to the job POST request does not seem to contain a result key")
        self.assertEqual(response["result"], "accepted", "Result is not 'accepted'")

        self.assertIn("uid", response, "The response to the job POST request does not seem to contain an uid key")

        self._uid = response["uid"]

    def test_get_compiserv_job(self):
        """
        Ensure that GET'ing the status of a compilation job seems to work as expected.
        Mocks the remote compilation server.
        """
        rv = self.app.post('/weblab/web/compiserv/queue/armc', data='cprogramsource')
        rv = self.app.get('/weblab/web/compiserv/queue/{0}'.format(self._uid))
        resp = json.loads(rv.data)

        self.assertIsNotNone(resp, "Resp is None")
        self.assertIn("state", resp, "The response to the GET request does not seem to contain a 'status' key")
        # self.assertEqual(resp["state"], "done", "The reported state is not 'done'")

    # def test_retrieve_result(self):
    #     """
    #     Ensure that we can retrieve the binary file etc.
    #     """
    #     rv = self.app.post('/weblab/web/compiserv/queue/armc', data='cprogramsource')
    #     rv = self.app.get('/weblab/web/compiserv/queue/{0}'.format("20+abcdef"))
    #
    #     # This call is meant to be carried out internally (by the experiment server itself),
    #     # once the file is ready.
    #     rv = self.app.get('/weblab/web/compiserv/result/{0}/outputfile'.format("20+abcdef"))
    #
    #     # Ensure that it returns a file indeed.
    #     self.assertEqual(rv.status_code, 200, "Result is not 200")
    #     self.assertEqual(rv.data, "Binary File Contents")
    #
    #     # This call is also meant to be carried out internally (by the experiment server),
    #     # once the file is ready.
    #     rv = self.app.get('/weblab/web/compiserv/result/{0}/logfile'.format("20+abcdef"))
    #
    #     # Ensure that it returns a file indeed.
    #     self.assertEqual(rv.status_code, 200, "Result is not 200")
    #     self.assertEqual(rv.data, "Log File Contents")
    #
    # def test_retrieve_result_reports_error_if_not_exists(self):
    #     """
    #     Ensure that if the job doesn't exist, an error is reported in JSON.
    #     """
    #
    #     # This call is meant to be carried out internally (by the experiment server itself),
    #     # once the file is ready.
    #     rv = self.app.get('/weblab/web/compiserv/result/{0}/outputfile'.format("21+abcdef"))
    #     self.assertEqual(rv.status_code, 200, "Result is not 200")
    #     jsresp = json.loads(rv.data)
    #     self.assertEqual(jsresp['result'], 'error', 'Result is not error')
    #
    #     rv = self.app.get('/weblab/web/compiserv/result/{0}/logfile'.format("21+abcdef"))
    #     self.assertEqual(rv.status_code, 200, "Result is not 200")
    #     jsresp = json.loads(rv.data)
    #     self.assertEqual(jsresp['result'], 'error', 'Result is not error')
    #
    # def test_retrieve_result_reports_error_if_pending(self):
    #     """
    #     Ensure that if the job hasn't finished, an error is reported in JSON.
    #     """
    #     rv = self.app.post('/weblab/web/compiserv/queue/armc', data='cprogramsource')
    #     rv = self.app.get('/weblab/web/compiserv/queue/{0}'.format("20+abcdef"))  # This won't finish.
    #
    #     # This call is meant to be carried out internally (by the experiment server itself),
    #     # once the file is ready.
    #     rv = self.app.get('/weblab/web/compiserv/result/{0}/outputfile'.format("20+abcdef"))
    #     self.assertEqual(rv.status_code, 200, "Result is not 200")
    #     jsresp = json.loads(rv.data)
    #     self.assertEqual(jsresp['result'], 'error', 'Result is not error')
    #
    #     rv = self.app.get('/weblab/web/compiserv/result/{0}/logfile'.format("20+abcdef"))
    #     self.assertEqual(rv.status_code, 200, "Result is not 200")
    #     jsresp = json.loads(rv.data)
    #     self.assertEqual(jsresp['result'], 'error', 'Result is not error')

    def tearDown(self):
        """
        Shutdown the WebLab instance that we have started for the test.
        """
        rv = self.app.post('/weblab/login', data=dict(username='any', password='password'))
        self.assertEqual(rv.status_code, 302, "Login POST with right pass does not return 302")

        self.handler.stop()