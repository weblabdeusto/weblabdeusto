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
from __future__ import print_function, unicode_literals

import sys
import time
import unittest

from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY

from weblab.data.command import Command
from weblab.data.experiments import ExperimentId, RunningReservationResult
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.core.reservations import Reservation

DEBUG = False

def debug(msg):
    if DEBUG:
        print()
        print("DEBUG:", msg)
        print()
        sys.stdout.flush()

class AbstractFederatedWebLabDeustoTestCase(object):
    def setUp(self):
        # Clean the global registry of servers
        GLOBAL_REGISTRY.clear()

        CONSUMER_CONFIG_PATH  = self.FEDERATED_DEPLOYMENTS + '/consumer/'
        PROVIDER1_CONFIG_PATH = self.FEDERATED_DEPLOYMENTS + '/provider1/'
        PROVIDER2_CONFIG_PATH = self.FEDERATED_DEPLOYMENTS + '/provider2/'

        self.consumer_handler  = load_dir(CONSUMER_CONFIG_PATH).load_process('consumer_machine', 'main_instance' )
        self.provider1_handler = load_dir(PROVIDER1_CONFIG_PATH).load_process('provider1_machine', 'main_instance' )
        self.provider2_handler = load_dir(PROVIDER2_CONFIG_PATH).load_process('provider2_machine', 'main_instance' )
        
        self.consumer_client  = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 18345)

        self.provider1_client  = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 28345)

        self.provider2_client  = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % 38345)

        # dummy1: deployed in consumer, provider1, provider2
        self.dummy1 = ExperimentId("dummy1", "Dummy experiments")
        # dummy2: deployed in consumer
        self.dummy2 = ExperimentId("dummy2", "Dummy experiments")
        # dummy3: deployed in provider1 as "dummy3_with_other_name"
        self.dummy3 = ExperimentId("dummy3", "Dummy experiments")
        # dummy4: deployed in provider2
        self.dummy4 = ExperimentId("dummy4", "Dummy experiments")

    def tearDown(self):
        self.consumer_handler.stop()
        self.provider1_handler.stop()
        self.provider2_handler.stop()
        time.sleep(1)

    #
    # This test may take even 20-30 seconds; therefore it is not splitted
    # into subtests (the setup and teardown are long)
    #
    def test_federated_experiment(self):
        debug("Test test_federated_experiment starts")

        #######################################################
        #
        #   Local testing  (to check that everything is right)
        #
        #   We enter as a student of Consumer, and we ask for an
        #   experiment that only the Consumer university has
        #   (dummy2).
        #
        session_id = self.consumer_client.login('fedstudent1', 'password')

        reservation_id = self._test_reservation(session_id, self.dummy2, 'Consumer', True, True)
        self._wait_multiple_reservations(20, session_id, [ reservation_id ], [0])
        reservation_result = self.consumer_client.get_experiment_use_by_id(session_id, reservation_id)
        self.assertTrue(reservation_result.is_finished())
        self._find_command(reservation_result, 'Consumer')


        #######################################################
        #
        #   Simple federation
        #
        #   Now we ask for an experiment that only Provider 1
        #   has. There is no load balance, neither
        #   subcontracting
        #
        reservation_id = self._test_reservation(session_id, self.dummy3, 'Provider 1', True, True)
        self._wait_multiple_reservations(20, session_id, [ reservation_id ], [0])
        reservation_result = self.consumer_client.get_experiment_use_by_id(session_id, reservation_id)
        self.assertTrue(reservation_result.is_finished())
        self._find_command(reservation_result, 'Provider 1')

        #######################################################
        #
        #   Subcontracted federation
        #
        #   Now we ask for an experiment that only Provider 2
        #   has. There is no load balance, but Consumer will
        #   contact Provider 1, which will contact Provider 2
        #
        reservation_id = self._test_reservation(session_id, self.dummy4, 'Provider 2', True, True)
        self._wait_multiple_reservations(20, session_id, [ reservation_id ], [0])
        reservation_result = self.consumer_client.get_experiment_use_by_id(session_id, reservation_id)
        self.assertTrue(reservation_result.is_finished())
        self._find_command(reservation_result, 'Provider 2')

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
        reservation_results = self.consumer_client.get_experiment_uses_by_id(session_id, reservation_ids)

        self.assertEquals(RunningReservationResult(), reservation_results[0])
        self.assertEquals(RunningReservationResult(), reservation_results[1])
        self.assertEquals(RunningReservationResult(), reservation_results[2])


        #
        # What if one of them goes out and another comes? Is the load of experiments balanced correctly?
        #
        self.consumer_client.finished_experiment(reservation_id2)

        # Wait a couple of seconds to check that it has been propagated
        self._wait_multiple_reservations(20, session_id, reservation_ids, [1])

        reservation_results = self.consumer_client.get_experiment_uses_by_id(session_id, reservation_ids)

        # The other two are still running
        self.assertEquals(RunningReservationResult(), reservation_results[0])
        self.assertEquals(RunningReservationResult(), reservation_results[2])
        
        # But the one finished is actually finished
        self.assertTrue( reservation_results[1].is_finished() ) 
        self.assertEquals('Firefox', reservation_results[1].experiment_use.request_info['user_agent'])
        self.assertEquals(4, len(reservation_results[1].experiment_use.commands))
        self.assertEquals('Provider 1', reservation_results[1].experiment_use.commands[2].response.commandstring)

        reservation_id2b = self._test_reservation(session_id, self.dummy1, 'Provider 1', True, False)

        self.consumer_client.finished_experiment(reservation_id1)
        self._test_reservation(session_id, self.dummy1, 'Consumer', True, False)
        reservation_status = self.consumer_client.get_reservation_status(reservation_id3)
        provider2_reservation_id = reservation_status.remote_reservation_id

        self.consumer_client.finished_experiment(reservation_id3)
        self._test_reservation(session_id, self.dummy1, 'Provider 2', True, False)

        # Check for the other uses
        self._wait_multiple_reservations(70, session_id, reservation_ids, [0,2])

        reservation_results = self.consumer_client.get_experiment_uses_by_id(session_id, reservation_ids)
        self.assertTrue( reservation_results[0].is_finished() )
        self.assertEquals('Chrome', reservation_results[0].experiment_use.request_info['user_agent'])
        self.assertEquals('Consumer', reservation_results[0].experiment_use.commands[2].response.commandstring)

        self.assertTrue( reservation_results[2].is_finished() )
        self.assertEquals('Safari', reservation_results[2].experiment_use.request_info['user_agent'])
        self.assertEquals('Provider 2', reservation_results[2].experiment_use.commands[2].response.commandstring)

        provider2_session_id = self.provider2_client.login('provider1', 'password')
        provider2_result = self.provider2_client.get_experiment_use_by_id(provider2_session_id, provider2_reservation_id)
        self.assertTrue(provider2_result.is_finished())
        self.assertEquals('Safari', provider2_result.experiment_use.request_info['user_agent'])

        #
        # What if another 2 come in? What is the position of their queues?
        #

        reservation_4 = self._test_reservation(session_id, self.dummy1, '', False, False)
        reservation_status = self.consumer_client.get_reservation_status(reservation_4)
        self.assertEquals(Reservation.WAITING, reservation_status.status)
        self.assertEquals(0, reservation_status.position)

        reservation_5 = self._test_reservation(session_id, self.dummy1, '', False, False)
        reservation_status = self.consumer_client.get_reservation_status(reservation_5)
        self.assertEquals(Reservation.WAITING, reservation_status.status)
        self.assertEquals(1, reservation_status.position)

        #
        # Once again, freeing a session affects them?
        #
        self.consumer_client.finished_experiment(reservation_id2b)
        self._wait_reservation(reservation_4, 'Provider 1', True)

        self.consumer_client.finished_experiment(reservation_4)
        self._wait_reservation(reservation_5, 'Provider 1', True)

        # Check for the other uses
        for _ in range(50):
            time.sleep(0.5)
            # Checking every half second
            results = self.consumer_client.get_experiment_uses_by_id(session_id, (reservation_id2b, reservation_4))
            if results[0].is_finished() and results[1].is_finished():
                break

        final_reservation_results = self.consumer_client.get_experiment_uses_by_id(session_id, (reservation_id2b, reservation_4))
        self.assertTrue(final_reservation_results[0].is_finished())
        self.assertTrue(final_reservation_results[1].is_finished())
        self.assertEquals('Provider 1', final_reservation_results[0].experiment_use.commands[2].response.commandstring)
        self.assertEquals('Provider 1', final_reservation_results[1].experiment_use.commands[2].response.commandstring)

        debug("Test test_federated_experiment finishes successfully")

    def _wait_multiple_reservations(self, times, session_id, reservation_ids, reservations_to_wait):
        for _ in range(times):
            time.sleep(0.5)
            # Checking every half second
            results = self.consumer_client.get_experiment_uses_by_id(session_id, reservation_ids)
            all_finished = True

            for reservation_to_wait in reservations_to_wait:
                all_finished = all_finished and results[reservation_to_wait].is_finished()

            if all_finished:
                break

    def _find_command(self, reservation_result, expected_response):
        found = False
        commands = reservation_result.experiment_use.commands
        for command in commands:
            if command.command.commandstring == 'server_info':
                found = True
                response = command.response.commandstring
                self.assertEquals(expected_response, response, "Message %s not found in commands %s; instead found %s" % (expected_response, commands, response))
        self.assertTrue(found, "server_info not found in commands")

    def _test_reservation(self, session_id, experiment_id, expected_server_info, wait, finish, user_agent = None):
        debug("Reserving with session_id %r a experiment %r; will I wait? %s; will I finish? %s" % (session_id, experiment_id, wait, finish))
        reservation_status = self.consumer_client.reserve_experiment(session_id, experiment_id, "{}", "{}", user_agent = user_agent)

        reservation_id = reservation_status.reservation_id

        if not wait:
            if finish:
                debug("Finishing... %r" % reservation_id)
                self.consumer_client.finished_experiment(reservation_id)
            debug("Not waiting... %r" % reservation_id)
            return reservation_id

        reservation_id = self._wait_reservation(reservation_id, expected_server_info, finish)
        debug("Finished waiting... %r" % reservation_id)
        return reservation_id

    def _wait_reservation(self, reservation_id, expected_server_info, finish):
        max_timeout = 10
        initial_time = time.time()

        reservation_status = self.consumer_client.get_reservation_status(reservation_id)
        while reservation_status.status in (Reservation.WAITING, Reservation.WAITING_CONFIRMATION):
            if time.time() - initial_time > max_timeout:
                self.fail("Waiting too long in the queue for %s" % expected_server_info)
            time.sleep(0.1)
            reservation_status = self.consumer_client.get_reservation_status(reservation_id)

        self.assertEquals(Reservation.CONFIRMED, reservation_status.status)

        experiment_reservation_id = reservation_status.remote_reservation_id
        if experiment_reservation_id.id == '':
            experiment_reservation_id = reservation_id

        client = WebLabDeustoClient( reservation_status.url )

        response = client.send_command(experiment_reservation_id, Command("server_info"))
        self.assertEquals(expected_server_info, response.get_command_string())

        if finish:
            self.consumer_client.finished_experiment(reservation_id)

        return reservation_id

class SqlFederatedWebLabDeustoTestCase(AbstractFederatedWebLabDeustoTestCase, unittest.TestCase):
    FEDERATED_DEPLOYMENTS = 'test/deployments/federated_basic_sql'
    IS_SQL = True

try:
    import redis
    assert redis is not None
except ImportError:
    REDIS_AVAILABLE = False
else:
    REDIS_AVAILABLE = True

if REDIS_AVAILABLE:
    class RedisFederatedWebLabDeustoTestCase(AbstractFederatedWebLabDeustoTestCase, unittest.TestCase):
        FEDERATED_DEPLOYMENTS = 'test/deployments/federated_basic_redis'
        IS_SQL = False

def suite():
    suites = [unittest.makeSuite(SqlFederatedWebLabDeustoTestCase)]
    if REDIS_AVAILABLE:
        suites.append(unittest.makeSuite(RedisFederatedWebLabDeustoTestCase))
    else:
        print("redis not available. Skipping redis-based federation integration tests", file = sys.stderr)
    return unittest.TestSuite( suites )

if __name__ == '__main__':
    unittest.main()


