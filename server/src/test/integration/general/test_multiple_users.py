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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import time
import unittest

from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY

import weblab.configuration_doc as configuration_doc

import weblab.data.command as Command
import weblab.experiment.util as ExperimentUtil
import weblab.core.reservations as Reservation
import weblab.core.server as UserProcessingServer

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient

from test.util.module_disposer import case_uses_module

# Abstract
class IntegrationMultipleUsersTestCase(object):
    def setUp(self):
        self.global_config = load_dir(self.DEPLOYMENT_DIR)

        self.process_handlers = []
        for process in self.PROCESSES:
            process_handler = self.global_config.load_process('myhost', process)
            self.process_handlers.append(process_handler)

        self.core_server       = GLOBAL_REGISTRY[self.CORE_ADDRESS]
        self.experiment_dummy1 = GLOBAL_REGISTRY[self.EXPERIMENT_DUMMY1]
        self.experiment_dummy2 = GLOBAL_REGISTRY[self.EXPERIMENT_DUMMY2]

        self.core_config = self.core_server.config

        self.client = WebLabDeustoClient('http://localhost:%s/weblab/' % self.core_config[configuration_doc.CORE_FACADE_PORT])

    def tearDown(self):
        GLOBAL_REGISTRY.clear()

        for process_handler in self.process_handlers:
            process_handler.stop()

    def test_single_uses_timeout(self):
        # 6 users get into the system
        session_id1 = self.client.login('intstudent1','password')
        session_id2 = self.client.login('intstudent2','password')
        session_id3 = self.client.login('intstudent3','password')
        session_id4 = self.client.login('intstudent4','password')
        session_id5 = self.client.login('intstudent5','password')
        session_id6 = self.client.login('intstudent6','password')

        # they all have access to the ud-fpga experiment
        experiments1 = self.client.list_experiments(session_id1)
        dummy_experiments1 = [ exp.experiment for exp in experiments1 if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy_experiments1), 1 )

        experiments2 = self.client.list_experiments(session_id2)
        dummy_experiments2 = [ exp.experiment for exp in experiments2 if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy_experiments2), 1 )

        experiments3 = self.client.list_experiments(session_id3)
        dummy_experiments3 = [ exp.experiment for exp in experiments3 if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy_experiments3), 1 )

        experiments4 = self.client.list_experiments(session_id4)
        dummy_experiments4 = [ exp.experiment for exp in experiments4 if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy_experiments4), 1 )

        experiments5 = self.client.list_experiments(session_id5)
        dummy_experiments5 = [ exp.experiment for exp in experiments5 if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy_experiments5), 1 )

        experiments6 = self.client.list_experiments(session_id6)
        dummy_experiments6 = [ exp.experiment for exp in experiments6 if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy_experiments6), 1 )

        # 3 users try to reserve the experiment
        status1 = self.client.reserve_experiment(session_id1, dummy_experiments1[0].to_experiment_id(), "{}", "{}")
        reservation_id1 = status1.reservation_id

        status2 = self.client.reserve_experiment(session_id2, dummy_experiments2[0].to_experiment_id(), "{}", "{}")
        reservation_id2 = status2.reservation_id

        status3 = self.client.reserve_experiment(session_id3, dummy_experiments3[0].to_experiment_id(), "{}", "{}")
        reservation_id3 = status3.reservation_id

        # wait until it is reserved
        short_time = 0.1
        times      = 10.0 / short_time

        while times > 0:
            time.sleep(short_time)
            new_status = self.client.get_reservation_status(reservation_id1)
            if not isinstance(new_status, Reservation.WaitingConfirmationReservation):
                break
            times -= 1

        # first user got the device. The other two are in WaitingReservation
        reservation1 = self.client.get_reservation_status(reservation_id1)
        self.assertTrue(isinstance(reservation1, Reservation.ConfirmedReservation))

        reservation2 = self.client.get_reservation_status(reservation_id2)
        self.assertTrue(isinstance(reservation2, Reservation.WaitingReservation))
        self.assertEquals( 0, reservation2.position)

        reservation3 = self.client.get_reservation_status(reservation_id3)
        self.assertTrue(isinstance(reservation3, Reservation.WaitingReservation))
        self.assertEquals( 1, reservation3.position)

        # Another user tries to reserve the experiment. He goes to the WaitingReservation, position 2
        status4 = self.client.reserve_experiment(session_id4, dummy_experiments4[0].to_experiment_id(), "{}", "{}")

        reservation_id4 = status4.reservation_id

        reservation4 = self.client.get_reservation_status(reservation_id4)
        self.assertTrue(isinstance( reservation4, Reservation.WaitingReservation))
        self.assertEquals( 2, reservation4.position)

        # The state of other users does not change
        reservation1 = self.client.get_reservation_status(reservation_id1)
        self.assertTrue(isinstance( reservation1, Reservation.ConfirmedReservation))

        reservation2 = self.client.get_reservation_status(reservation_id2)
        self.assertTrue(isinstance( reservation2, Reservation.WaitingReservation))
        self.assertEquals( 0, reservation2.position)

        reservation3 = self.client.get_reservation_status(reservation_id3)
        self.assertTrue(isinstance(reservation3, Reservation.WaitingReservation))
        self.assertEquals( 1, reservation3.position )

        # The user number 2 frees the experiment
        self.client.finished_experiment(reservation_id2)

        # Whenever he tries to do poll or send_command, he receives an exception
        try:
            time.sleep(1)
            self.client.poll(reservation_id2)
            self.client.poll(reservation_id2)
            self.client.poll(reservation_id2)
        except Exception as e:
            pass # All right :-)
            self.assertTrue("does not have any experiment" in repr(e))
        else:
            self.fail("Expected exception when polling")

        # send a program
        CONTENT = "content of the program DUMMY1"
        self.client.send_file(reservation_id1, ExperimentUtil.serialize(CONTENT), 'program')


        # We need to wait for the programming to finish.
        response = self.client.send_command(reservation_id1, Command.Command("STATE"))
        self.assertEquals("STATE", response.commandstring)

        self.client.logout(session_id1)

@case_uses_module(UserProcessingServer)
class IntegrationMultipleUsers_Direct_Memory_TestCase(IntegrationMultipleUsersTestCase, unittest.TestCase):
    DEPLOYMENT_DIR = 'test/deployments/integration_tests/case01_direct/'
    PROCESSES = ['myprocess']
    CORE_ADDRESS = 'mycore:myprocess@myhost'
    EXPERIMENT_DUMMY1 = 'experiment_dummy1:myprocess@myhost'
    EXPERIMENT_DUMMY2 = 'experiment_dummy1:myprocess@myhost'


@case_uses_module(UserProcessingServer)
class IntegrationMultipleUsers_Http_Memory_TestCase(IntegrationMultipleUsersTestCase, unittest.TestCase):
    DEPLOYMENT_DIR = 'test/deployments/integration_tests/case01_http/'
    PROCESSES = ['myprocess1', 'myprocess2', 'myprocess3']
    CORE_ADDRESS = 'mycore:myprocess1@myhost'
    EXPERIMENT_DUMMY1 = 'experiment_dummy1:myprocess3@myhost'
    EXPERIMENT_DUMMY2 = 'experiment_dummy1:myprocess3@myhost'


def suite():
    return unittest.TestSuite( (
            unittest.makeSuite(IntegrationMultipleUsers_Direct_Memory_TestCase),
            unittest.makeSuite(IntegrationMultipleUsers_Http_Memory_TestCase),
        ))

if __name__ == '__main__':
    unittest.main()


