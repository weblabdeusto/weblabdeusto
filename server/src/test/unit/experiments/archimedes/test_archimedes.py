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
# Author: Luis Rodriguez-Gil <luis.rodriguezgil@deusto.es>
#
from __future__ import print_function, unicode_literals
import base64
import json
import unittest
import threading
import time
from mock import patch, PropertyMock, MagicMock
from experiments.archimedes import Archimedes

from voodoo.configuration import ConfigurationManager
from voodoo.sessions.session_id import SessionId


class TestArchimedes(unittest.TestCase):

    def setUp(self):
        # Initialize the experiment for testing.
        # We set the archimedes_real_device setting to False so that
        # it doesn't attempt to contact the real ip.
        self.cfg_manager = ConfigurationManager()
        self.cfg_manager._set_value("archimedes_real_device", False)
        self.cfg_manager._set_value("archimedes_instances", {"default": "http://localhost:8000", "second": "http://localhost:8001"})
        self.experiment = Archimedes(None, None, self.cfg_manager)
        self.lab_session_id = SessionId('my-session-id')

    def tearDown(self):
        self.experiment.do_dispose()

    def test_start(self):
        m = MagicMock(return_value="")
        self.experiment._send = m
        start = self.experiment.do_start_experiment("{}", "{}")

        assert m.mock_calls[0][1][1] == "up"
        assert m.mock_calls[1][1][1] == "up"

    def test_unknown_instance(self):
        """
        Check that it replies an error if the instance isn't in the config.
        """
        self.cfg_manager = ConfigurationManager()
        self.cfg_manager._set_value("archimedes_instances", {"first": "http://localhost:8000", "second": "http://localhost:8001"})
        self.experiment = Archimedes(None, None, self.cfg_manager)
        start = self.experiment.do_start_experiment("{}", "{}")

        up_resp = self.experiment.do_send_command_to_device("UP")
        assert up_resp.startswith("ERROR:")

        up_resp = self.experiment.do_send_command_to_device("default:UP")
        assert up_resp.startswith("ERROR:")

    def test_control_ball_commands(self):
        start = self.experiment.do_start_experiment("{}", "{}")
        up_resp = self.experiment.do_send_command_to_device("UP")
        down_resp = self.experiment.do_send_command_to_device("DOWN")
        slow_resp = self.experiment.do_send_command_to_device("SLOW")

    def test_basic_data_commands(self):
        start = self.experiment.do_start_experiment("{}", "{}")
        level_resp = self.experiment.do_send_command_to_device("LEVEL")
        assert float(level_resp) == 1200

        load_resp = self.experiment.do_send_command_to_device("LOAD")
        assert float(load_resp) == 1300

    def test_advanced_data_commands(self):
        start = self.experiment.do_start_experiment("{}", "{}")
        image_resp = self.experiment.do_send_command_to_device("IMAGE")
        dec = base64.b64decode(image_resp)
        assert len(dec) > 100

        plot_resp = self.experiment.do_send_command_to_device("PLOT")

        f = file("/tmp/img.html", "w+")
        f.write("""
            <html><body><img alt="embedded" src="data:image/jpg;base64,%s"/></body></html>
            """ % (image_resp)
        )
        f.close()

    def test_explicit_instance_commands(self):
        """
        Test that commands can be sent to a specific instance.
        """
        start = self.experiment.do_start_experiment("{}", "{}")
        up_resp = self.experiment.do_send_command_to_device("default:UP")
        down_resp = self.experiment.do_send_command_to_device("default:DOWN")
        slow_resp = self.experiment.do_send_command_to_device("default:SLOW")
        level_resp = self.experiment.do_send_command_to_device("default:LEVEL")
        assert float(level_resp) == 1200
        load_resp = self.experiment.do_send_command_to_device("default:LOAD")
        assert float(load_resp) == 1300

    def test_allinfo_command(self):
        start = self.experiment.do_start_experiment("{}", "{}")
        resp = self.experiment.do_send_command_to_device("ALLINFO:default")
        r = json.loads(resp)
        assert float(r["default"]["level"]) == 1200
        assert float(r["default"]["load"]) == 1300

    def test_allinfo_command_multiple(self):
        start = self.experiment.do_start_experiment("{}", "{}")
        resp = self.experiment.do_send_command_to_device("ALLINFO:default:second")
        r = json.loads(resp)
        assert float(r["default"]["level"]) == 1200
        assert float(r["default"]["load"]) == 1300

        assert float(r["second"]["level"]) == 1200
        assert float(r["second"]["load"]) == 1300

    # The following test is commented out for now because it is no longer a "challenge".
    # We now rely on a permanent thread-pool.
    #
    # def test_dispose_cleans_threads(self):
    #     """
    #     Archimedes Start creates a thread pool. Ensure that calling Dispose clears every thread.
    #     """
    #
    #     time.sleep
    #
    #     initialThreads = len(threading.enumerate())
    #     self.experiment.do_start_experiment("{}", "{}")
    #     self.experiment.do_dispose()
    #
    #     # TODO: This time should be *at most* 20 seconds. Ideally some kind of limited-time .join.
    #     # Or similar.
    #     time.sleep(20)
    #
    #     afterThreads = len(threading.enumerate())
    #     self.assertEqual(initialThreads, afterThreads, "all threads destroyed")


def suite():
    return unittest.TestSuite(
        (
            unittest.makeSuite(TestArchimedes)
        )
    )



if __name__ == '__main__':
    unittest.main()
