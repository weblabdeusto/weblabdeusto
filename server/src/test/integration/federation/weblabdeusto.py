#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
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

import time
import unittest

import voodoo.gen.loader.ServerLoader as ServerLoader

from weblab.data.command import Command
from weblab.data.experiments import ExperimentId, WaitingReservationResult, RunningReservationResult
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.core.reservations import Reservation

FEDERATED_DEPLOYMENTS = 'test/deployments/federated_basic'

CONSUMER_CONFIG_PATH  = FEDERATED_DEPLOYMENTS + '/consumer/'
PROVIDER1_CONFIG_PATH = FEDERATED_DEPLOYMENTS + '/provider1/'
PROVIDER2_CONFIG_PATH = FEDERATED_DEPLOYMENTS + '/provider2/'

class FederatedWebLabDeustoTestCase(unittest.TestCase):
    def setUp(self):
        self.server_loader     = ServerLoader.ServerLoader()

        self.consumer_handler  = self.server_loader.load_instance( CONSUMER_CONFIG_PATH,   'consumer_machine', 'main_instance' )
        self.provider1_handler = self.server_loader.load_instance( PROVIDER1_CONFIG_PATH,  'provider1_machine', 'main_instance' )
        self.provider2_handler = self.server_loader.load_instance( PROVIDER2_CONFIG_PATH,  'provider2_machine', 'main_instance' )

        self.consumer_login_client = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 18645 )
        self.consumer_core_client  = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 18345 )

        self.provider1_login_client = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 28645 )
        self.provider1_core_client  = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 28345 )

        self.provider2_login_client = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 38645 )
        self.provider2_core_client  = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 38345 )

        # dummy1: deployed in consumer, provider1, provider2
        self.dummy1 = ExperimentId("dummy1", "Dummy experiments")
        # dummy2: deployed in consumer
        self.dummy2 = ExperimentId("dummy2", "Dummy experiments")
        # dummy3: deployed in provider1
        self.dummy3 = ExperimentId("dummy3", "Dummy experiments")
        # dummy4: deployed in provider2
        self.dummy4 = ExperimentId("dummy4", "Dummy experiments")

    def tearDown(self):
        self.consumer_handler.stop()
        self.provider1_handler.stop()
        self.provider2_handler.stop()

    #
    # This test may take even 20-30 seconds; therefore it is not splitted
    # into subtests (the setup and teardown are long)
    #
    def test_federated_experiment(self):
        #######################################################
        #
        #   Local testing  (to check that everything is right)
        #
        #   We enter as a student of Consumer, and we ask for an
        #   experiment that only the Consumer university has
        #   (dummy2).
        #
        session_id = self.consumer_login_client.login('fedstudent1', 'password')

        self._test_reservation(session_id, self.dummy2, 'Consumer', True, True)

        #######################################################
        #
        #   Simple federation
        #
        #   Now we ask for an experiment that only Provider 1
        #   has. There is no load balance, neither
        #   subcontracting
        #
        self._test_reservation(session_id, self.dummy3, 'Provider 1', True, True)

        #######################################################
        #
        #   Subcontracted federation
        #
        #   Now we ask for an experiment that only Provider 2
        #   has. There is no load balance, but Consumer will
        #   contact Provider 1, which will contact Provider 2
        #
        self._test_reservation(session_id, self.dummy4, 'Provider 2', True, True)

        #######################################################
        #
        #   Cross-domain load balancing
        #
        #   Now we ask for an experiment that Consumer has,
        #   but also Provider 1 and Provider 2.
        #

        reservation_id1 = self._test_reservation(session_id, self.dummy1, 'Consumer',  True, False,  user_agent = 'Chrome')
        reservation_id2 = self._test_reservation(session_id, self.dummy1, 'Provider 1', True, False, user_agent = 'Firefox')
        reservation_id3 = self._test_reservation(session_id, self.dummy1, 'Provider 2', True, False, user_agent = 'Safari')

        reservation_ids = (reservation_id1, reservation_id2, reservation_id3)
        reservation_results = self.consumer_core_client.get_experiment_uses_by_id(session_id, reservation_ids)

        self.assertEquals(RunningReservationResult(), reservation_results[0])
        self.assertEquals(RunningReservationResult(), reservation_results[1])
        self.assertEquals(RunningReservationResult(), reservation_results[2])


        #
        # What if one of them goes out and another comes? Is the load of experiments balanced correctly?
        #
        self.consumer_core_client.finished_experiment(reservation_id2)

        # Wait a couple of seconds to check that it is propagated
        time.sleep(1)

        reservation_results = self.consumer_core_client.get_experiment_uses_by_id(session_id, reservation_ids)

        # The other two are still running
        self.assertEquals(RunningReservationResult(), reservation_results[0])
        self.assertEquals(RunningReservationResult(), reservation_results[2])
        
        # But the one finished is actually finished
        self.assertTrue( reservation_results[1].is_finished() ) 
        self.assertEquals('Firefox', reservation_results[1].experiment_use.request_info['user_agent'])
        self.assertEquals(4, len(reservation_results[1].experiment_use.commands))
        self.assertEquals('Provider 1', reservation_results[1].experiment_use.commands[2].response.commandstring)

        reservation_id2b = self._test_reservation(session_id, self.dummy1, 'Provider 1', True, False)

        self.consumer_core_client.finished_experiment(reservation_id1)
        self._test_reservation(session_id, self.dummy1, 'Consumer', True, False)

        self.consumer_core_client.finished_experiment(reservation_id3)
        self._test_reservation(session_id, self.dummy1, 'Provider 2', True, False)

        time.sleep(1)

        reservation_results = self.consumer_core_client.get_experiment_uses_by_id(session_id, reservation_ids)
        self.assertTrue( reservation_results[0].is_finished() )
        self.assertEquals('Chrome', reservation_results[0].experiment_use.request_info['user_agent'])
        self.assertEquals('Consumer', reservation_results[0].experiment_use.commands[2].response.commandstring)
        self.assertTrue( reservation_results[2].is_finished() )
        self.assertEquals('Safari', reservation_results[2].experiment_use.request_info['user_agent'])
        self.assertEquals('Provider 2', reservation_results[2].experiment_use.commands[2].response.commandstring)

        #
        # What if another 2 come in? What is the position of their queues?
        #

        reservation_4 = self._test_reservation(session_id, self.dummy1, '', False, False)
        reservation_status = self.consumer_core_client.get_reservation_status(reservation_4)
        self.assertEquals(Reservation.WAITING, reservation_status.status)
        self.assertEquals(0, reservation_status.position)

        reservation_5 = self._test_reservation(session_id, self.dummy1, '', False, False)
        reservation_status = self.consumer_core_client.get_reservation_status(reservation_5)
        self.assertEquals(Reservation.WAITING, reservation_status.status)
        self.assertEquals(1, reservation_status.position)

        #
        # Once again, freeing a session affects them?
        #
        self.consumer_core_client.finished_experiment(reservation_id2b)
        self._wait_reservation(reservation_4, 'Provider 1', True)

        self.consumer_core_client.finished_experiment(reservation_4)
        self._wait_reservation(reservation_5, 'Provider 1', True)

    def _test_reservation(self, session_id, experiment_id, expected_server_info, wait, finish, user_agent = None):
        reservation_status = self.consumer_core_client.reserve_experiment(session_id, experiment_id, "{}", "{}", user_agent = user_agent)

        reservation_id = reservation_status.reservation_id

        if not wait:
            if finish:
                self.consumer_core_client.finished_experiment(reservation_id)
            return reservation_id

        return self._wait_reservation(reservation_id, expected_server_info, finish)

    def _wait_reservation(self, reservation_id, expected_server_info, finish):
        max_timeout = 10
        initial_time = time.time()

        reservation_status = self.consumer_core_client.get_reservation_status(reservation_id)
        while reservation_status.status in (Reservation.WAITING, Reservation.WAITING_CONFIRMATION):
            if time.time() - initial_time > max_timeout:
                self.fail("Waiting too long in the queue for %s" % expected_server_info)
            time.sleep(0.1)
            reservation_status = self.consumer_core_client.get_reservation_status(reservation_id)

        self.assertEquals(Reservation.CONFIRMED, reservation_status.status)

        experiment_reservation_id = reservation_status.remote_reservation_id
        if experiment_reservation_id.id == '':
            experiment_reservation_id = reservation_id

        client = WebLabDeustoClient( reservation_status.url )

        response = client.send_command(experiment_reservation_id, Command("server_info"))
        self.assertEquals(expected_server_info, response.get_command_string())

        if finish:
            self.consumer_core_client.finished_experiment(reservation_id)

        return reservation_id

def suite():
    suites = (unittest.makeSuite(FederatedWebLabDeustoTestCase), )
    return unittest.TestSuite( suites )

if __name__ == '__main__':
    unittest.main()


