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

import sys
import time
import unittest

import six

from voodoo.gen import load_dir, CoordAddress
from voodoo.gen.registry import GLOBAL_REGISTRY

import weblab.configuration_doc as configuration_doc

import weblab.data.command as Command
import weblab.data.server_type as ServerType
import weblab.experiment.util as ExperimentUtil
import weblab.lab.server as LaboratoryServer
import weblab.core.alive_users as AliveUsersCollection
import weblab.core.reservations as Reservation
import weblab.core.server as UserProcessingServer
import weblab.core.server as core_api

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient

from test.util.wlcontext import wlcontext
from test.util.ports import new as new_port
from test.util.module_disposer import case_uses_module

########################################################
# Case 001: a single instance of everything on a       #
# single instance of the WebLab, with two experiments #
########################################################

# Abstract
class Case001TestCase(object):
    def setUp(self):
        self.global_config = load_dir(self.DEPLOYMENT_DIR)

        self.process_handlers = []
        for process in self.PROCESSES:
            process_handler = self.global_config.load_process('myhost', process)
            self.process_handlers.append(process_handler)

        self.core_config = self.global_config.create_config(CoordAddress.translate(self.CORE_ADDRESS))
        self.client = WebLabDeustoClient('http://localhost:%s/weblab/' % self.core_config[configuration_doc.CORE_FACADE_PORT])

        self.experiment_dummy1 = GLOBAL_REGISTRY[self.EXPERIMENT_DUMMY1]
        self.experiment_dummy2 = GLOBAL_REGISTRY[self.EXPERIMENT_DUMMY2]

    def tearDown(self):
        GLOBAL_REGISTRY.clear()

        for process_handler in self.process_handlers:
            process_handler.stop()


    def test_single_uses_timeout(self):
        backup_poll_time           = configuration.core_experiment_poll_time
        backup_time_between_checks = self.cfg_manager.get_value('core_time_between_checks', AliveUsersCollection.DEFAULT_TIME_BETWEEN_CHECKS)
        try:
            self.cfg_manager._set_value('core_experiment_poll_time',1.5)
            self.cfg_manager._set_value('core_time_between_checks',1.5)
            self._single_use(logout = False, plus_async_use = False)
            time.sleep(self.cfg_manager.get_value('core_experiment_poll_time') + 0.3 + self.cfg_manager.get_value('core_time_between_checks'))
            self._single_use(logout = False, plus_async_use = False)
        finally:
            self.cfg_manager._set_value('core_experiment_poll_time',backup_poll_time)
            self.cfg_manager._set_value('core_time_between_checks',backup_time_between_checks)

    def test_simple_single_uses(self):
        for _ in range(1):
            self._single_use()
        self._single_use()
        self._single_use()

    def _wait_async_done(self, reservation_id, reqids):
        """
        _wait_async_done(session_id, reqids)
        Helper methods that waits for the specified asynchronous requests to be finished,
        and which asserts that they were successful. Note that it doesn't actually return
        their responses.
        @param reqids Tuple containing the request ids for the commands to check.
        @return Nothing
        """
        # Wait until send_async_file query is actually finished.
        reqsl = list(reqids)
        max_count = 15
        while len(reqsl) > 0:
            time.sleep(0.1)
            max_count -= 1
            if max_count == 0:
                raise Exception("Maximum time spent waiting async done")
            requests = self.client.check_async_command_status(reservation_id, tuple(reqsl))
            self.assertEquals(len(reqsl), len(requests))
            for rid, req in six.iteritems(requests):
                status = req[0]
                self.assertTrue(status in ("running", "ok", "error"))
                if status != "running":
                    self.assertEquals("ok", status, "Contents: " + req[1])
                    reqsl.remove(rid)


    def _get_async_response(self, reservation_id, reqid):
        """
        _get_async_response(reqids)
        Helper method that synchronously gets the response for the specified async request, asserting that
        it was successful.
        @param reqid The request identifier for the async request whose response we want
        @return Response to the request, if successful. None, otherwise.
        """
        # Wait until send_async_file query is actually finished.
        max_counter = 15
        while True:
            max_counter -= 1
            if max_counter == 0:
                raise Exception("Maximum times running get_async_response")
            time.sleep(0.1)
            requests = self.client.check_async_command_status(reservation_id, (reqid,))
            self.assertEquals(1, len(requests))
            self.assertTrue(reqid in requests)
            req = requests[reqid]
            status = req[0]
            self.assertTrue(status in ("running", "ok", "error"))
            if status != "running":
                self.assertEquals("ok", status, "Contents: " + req[1])
                return Command.Command(req[1])

    def _single_async_use(self, logout = True):
        session_id = self.client.login('fedstudent1', 'password')

        user_information = self.client.get_user_information(session_id)
        self.assertEquals( 'fedstudent1', user_information.login) 
        self.assertEquals( 'Name of federated student 1', user_information.full_name)
        self.assertEquals( 'weblab@deusto.es', user_information.email)

        experiments = self.client.list_experiments(session_id)
        self.assertEquals( 4, len(experiments))

        dummy1_experiments = [ exp.experiment for exp in experiments if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy1_experiments), 1)

        dummy1_experiment = dummy1_experiments[0]

        status = self.client.reserve_experiment(session_id, dummy1_experiment.to_experiment_id(), "{}", "{}")

        reservation_id = status.reservation_id

        # wait until it is reserved
        short_time = 0.1

        # Time extended from 9.0 to 15.0 because at times the test failed, possibly for that reason.
        times      = 15.0 / short_time

        while times > 0:
            new_status = self.client.get_reservation_status(reservation_id)
            if not isinstance(new_status, Reservation.WaitingConfirmationReservation) and not isinstance(new_status, Reservation.WaitingReservation):
                break
            times -= 1
            time.sleep(short_time)
        reservation = self.client.get_reservation_status(reservation_id)
        self.assertTrue(
                isinstance(reservation, Reservation.ConfirmedReservation),
                "Reservation %s is not Confirmed, as expected by this time" % reservation
            )

        # send the program again, but asynchronously. Though this should work, it is not really very customary
        # to send_file more than once in the same session. In fact, it is a feature which might get removed in
        # the future. When/if that happens, this will need to be modified.
        CONTENT = "content of the program FPGA"
        reqid = self.client.send_async_file(reservation_id, ExperimentUtil.serialize(CONTENT), 'program')

        # Wait until send_async_file query is actually finished.
        #self._get_async_response(session_id, reqid)
        self._wait_async_done(reservation_id, (reqid,))

        # We need to wait for the programming to finish, while at the same
        # time making sure that the tests don't dead-lock.
        reqid = self.client.send_async_command(reservation_id, Command.Command("STATE"))
        respcmd = self._get_async_response(reqid)
        response = respcmd.get_command_string()

        # Check that the current state is "Ready"
        self.assertEquals("STATE", response)


        reqid = self.client.send_async_command(reservation_id, Command.Command("ChangeSwitch on 0"))
        self._wait_async_done(reservation_id, (reqid,))

        reqid = self.client.send_async_command(reservation_id, Command.Command("ClockActivation on 250"))
        self._wait_async_done(reservation_id, (reqid,))

        if logout:
            self.client.logout(session_id)


    def _single_use(self, logout = True, plus_async_use = True):
        """
        Will use an experiment.
        @param logout If true, the user will be logged out after the use. Otherwise not.
        @param plus_async_use If true, after using the experiment synchronously, it will use it
        again using the asynchronous versions of the send_command and send_file requests.
        """
        self._single_sync_use(logout)
        if plus_async_use:
            self._single_async_use(logout)


    def _single_sync_use(self, logout = True):
        session_id = self.client.login('fedstudent1', 'password')

        user_information = self.client.get_user_information(session_id)
        self.assertEquals( 'fedstudent1', user_information.login) 
        self.assertEquals( 'Name of federated student 1', user_information.full_name)
        self.assertEquals( 'weblab@deusto.es', user_information.email)

        experiments = self.client.list_experiments(session_id)
        self.assertEquals( 4, len(experiments))

        dummy1_experiments = [ exp.experiment for exp in experiments if exp.experiment.name == 'dummy1' ]
        self.assertEquals( len(dummy1_experiments), 1)

        dummy1_experiment = dummy1_experiments[0]

        # reserve it
        status = self.client.reserve_experiment(session_id, dummy1_experiment.to_experiment_id(), "{}", "{}")

        reservation_id = status.reservation_id

        # wait until it is reserved
        short_time = 0.1
        times      = 13.0 / short_time

        while times > 0:
            new_status = self.client.get_reservation_status(reservation_id)
            if not isinstance(new_status, Reservation.WaitingConfirmationReservation) and not isinstance(new_status, Reservation.WaitingReservation):
                break
            times -= 1
            time.sleep(short_time)
        reservation = self.client.get_reservation_status(reservation_id)
        self.assertTrue(
                isinstance(reservation, Reservation.ConfirmedReservation),
                "Reservation %s is not Confirmed, as expected by this time" % reservation
            )


        # send a program synchronously (the "traditional" way)
        CONTENT = "content of the program FPGA"
        response = self.client.send_file(reservation_id, ExperimentUtil.serialize(CONTENT), 'program')
        self.assertEquals(response.commandstring, 'ack')

        response = self.client.send_command(reservation_id, Command.Command("STATE"))
        self.assertEquals(response.commandstring, 'STATE')

        response = self.client.send_command(reservation_id, Command.Command("ChangeSwitch on 0"))
        self.assertEquals(response.commandstring, "ChangeSwitch on 0")

#         end session
#         Note: Before async commands were implemented, this was actually done before
#         checking the commands sent. If it was that way for a reason, it might be
#         necessary to change it in the future.
        if logout:
            self.client.logout(session_id)


    def test_two_multiple_uses_of_different_devices(self):
        with wlcontext(self.real_ups):
            user1_session_id = core_api.login('student1','password')

        with wlcontext(self.real_ups, session_id = user1_session_id):
            user1_experiments = core_api.list_experiments()
            self.assertEquals( 5, len(user1_experiments))

            fpga_experiments = [ exp.experiment for exp in user1_experiments if exp.experiment.name == 'ud-fpga' ]
            self.assertEquals( len(fpga_experiments), 1)

            # reserve it
            status = core_api.reserve_experiment( fpga_experiments[0].to_experiment_id(), "{}", "{}")

            user1_reservation_id = status.reservation_id

        with wlcontext(self.real_ups):
            user2_session_id = core_api.login('student2','password')

        with wlcontext(self.real_ups, session_id = user2_session_id):
            user2_experiments = core_api.list_experiments()
            self.assertEquals( 7, len(user2_experiments))

            pld_experiments = [ exp.experiment for exp in user2_experiments if exp.experiment.name == 'ud-pld' ]
            self.assertEquals( len(pld_experiments), 1)

            # reserve it
            status = core_api.reserve_experiment(pld_experiments[0].to_experiment_id(), "{}", "{}")

            user2_reservation_id = status.reservation_id

        short_time = 0.1
        times      = 9.0 / short_time

        while times > 0:
            time.sleep(short_time)
            with wlcontext(self.real_ups, reservation_id = user1_reservation_id):
                new_status1 = core_api.get_reservation_status()

            with wlcontext(self.real_ups, reservation_id = user2_reservation_id):
                new_status2 = core_api.get_reservation_status()

            if not isinstance(new_status1, Reservation.WaitingConfirmationReservation):
                if not isinstance(new_status2, Reservation.WaitingConfirmationReservation):
                    break
            times -= 1

        with wlcontext(self.real_ups, reservation_id = user1_reservation_id):
            self.assertTrue(isinstance(core_api.get_reservation_status(), Reservation.ConfirmedReservation))
    
        with wlcontext(self.real_ups, reservation_id = user2_reservation_id):
            self.assertTrue(isinstance(core_api.get_reservation_status(), Reservation.ConfirmedReservation))


        with wlcontext(self.real_ups, reservation_id = user1_reservation_id):
            # send a program
            CONTENT1 = "content of the program FPGA"
            core_api.send_file(ExperimentUtil.serialize(CONTENT1), 'program')

            # We need to wait for the programming to finish.
            start_time = time.time()
            response = "STATE=not_ready"
            while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
                respcmd = core_api.send_command(Command.Command("STATE"))
                response = respcmd.get_command_string()
                time.sleep(0.2)

            # Check that the current state is "Ready"
            self.assertEquals("STATE=ready", response)

            core_api.send_command(Command.Command("ChangeSwitch off 1"))
            core_api.send_command(Command.Command("ClockActivation on 250"))

        with wlcontext(self.real_ups, reservation_id = user2_reservation_id):
            CONTENT2 = "content of the program PLD"
            core_api.send_file(ExperimentUtil.serialize(CONTENT2), 'program')

            # We need to wait for the programming to finish.
            start_time = time.time()
            response = "STATE=not_ready"
            while response in ("STATE=not_ready", "STATE=programming") and time.time() - start_time < XILINX_TIMEOUT:
                respcmd = core_api.send_command(Command.Command("STATE"))
                response = respcmd.get_command_string()
                time.sleep(0.2)

            # Check that the current state is "Ready"
            self.assertEquals("STATE=ready", response)

            core_api.send_command(Command.Command("ChangeSwitch on 0"))
            core_api.send_command(Command.Command("ClockActivation on 250"))

        # end session
        with wlcontext(self.real_ups, session_id = user1_session_id):
            core_api.logout()

        with wlcontext(self.real_ups, session_id = user2_session_id):
            core_api.logout()

        # Checking the commands sent
        self.assertEquals( 1, len(self.fake_impact1._paths))
        self.assertEquals( 1, len(self.fake_impact2._paths))
        self.assertEquals( CONTENT1, self.fake_impact1._paths[0])
        self.assertEquals( CONTENT2, self.fake_impact2._paths[0])

        initial_open  = 1
        initial_send  = 1
        initial_close = 1

        initial_total = initial_open + initial_send + initial_close

        # ChangeSwitch off 1
        self.assertEquals(
                (0 + initial_total,1),
                self.fake_serial_port1.dict['open'][0 + initial_open]
            )
        self.assertEquals(
                (1 + initial_total,4),
                self.fake_serial_port1.dict['send'][0 + initial_send]
            )
        self.assertEquals(
                (2 + initial_total,None),
                self.fake_serial_port1.dict['close'][0 + initial_close]
            )

        self.assertEquals(
                (0 + initial_total,1),
                self.fake_serial_port2.dict['open'][0 + initial_open]
            )
        self.assertEquals(
                (1 + initial_total,1),
                self.fake_serial_port2.dict['send'][0 + initial_send]
            )
        self.assertEquals(
                (2 + initial_total,None),
                self.fake_serial_port2.dict['close'][0 + initial_close]
            )

        # ClockActivation on 250
        self.assertEquals(
                (3 + initial_total,1),
                self.fake_serial_port1.dict['open'][1 + initial_open]
            )
        self.assertEquals(
                (4 + initial_total,32),
                self.fake_serial_port1.dict['send'][1 + initial_send]
            )

        self.assertEquals(
                (5 + initial_total,None),
                self.fake_serial_port1.dict['close'][1 + initial_close]
            )

        self.assertEquals(
                (3 + initial_total,1),
                self.fake_serial_port2.dict['open'][1 + initial_open]
            )
        self.assertEquals(
                (4 + initial_total,32),
                self.fake_serial_port2.dict['send'][1 + initial_send]
            )

        self.assertEquals(
                (5 + initial_total,None),
                self.fake_serial_port2.dict['close'][1 + initial_close]
            )

@case_uses_module(UserProcessingServer)
class Case001_Direct_TestCase(Case001TestCase, unittest.TestCase):
    DEPLOYMENT_DIR = 'test/deployments/integration_tests/case01_direct/'
    PROCESSES = ['myprocess']
    CORE_ADDRESS = 'mycore:myprocess@myhost'
    EXPERIMENT_DUMMY1 = 'experiment_dummy1:myprocess@myhost'
    EXPERIMENT_DUMMY2 = 'experiment_dummy1:myprocess@myhost'

@case_uses_module(UserProcessingServer)
class Case001_Http_TestCase(Case001TestCase, unittest.TestCase):
    DEPLOYMENT_DIR = 'test/deployments/integration_tests/case01_http/'
    PROCESSES = ['myprocess1', 'myprocess2', 'myprocess3']
    CORE_ADDRESS = 'mycore:myprocess1@myhost'
    EXPERIMENT_DUMMY1 = 'experiment_dummy1:myprocess3@myhost'
    EXPERIMENT_DUMMY2 = 'experiment_dummy1:myprocess3@myhost'

def suite():
    suites = (unittest.makeSuite(Case001_Direct_TestCase), unittest.makeSuite(Case001_Http_TestCase), )
    return unittest.TestSuite( suites )

if __name__ == '__main__':
    unittest.main()

