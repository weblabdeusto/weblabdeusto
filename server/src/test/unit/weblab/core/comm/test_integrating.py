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
import time
import sys
import unittest

from test.util.ports import new as new_port

import datetime

import weblab.configuration_doc as configuration_doc

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
import voodoo.sessions.session_id as SessionId
import weblab.data.dto.experiments as ExperimentAllowed
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as Category
from weblab.data.experiments import RunningReservationResult, FinishedReservationResult, CancelledReservationResult, ExperimentUsage, LoadedFileSent, CommandSent, ExperimentId
from voodoo.gen.coordinator.CoordAddress import CoordAddress

from weblab.data.dto.users import User
from weblab.data.dto.users import Role
import weblab.data.command as Command

import voodoo.configuration as ConfigurationManager
import test.unit.configuration as configuration

from test.util.module_disposer import uses_module

import weblab.core.comm.codes as UserProcessingRFCodes
import weblab.comm.server as RemoteFacadeServer
import weblab.core.comm.user_server as UserProcessingFacadeServer

import weblab.core.reservations as Reservation

import weblab.core.exc as coreExc

from test.unit.weblab.core.comm.test_user_manager import MockUPS

JSON_PORT = new_port()

class UserProcessingIntegratingRemoteFacadeManagerJSON(unittest.TestCase):
    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)

        self.configurationManager._set_value(configuration_doc.FACADE_TIMEOUT, 0.001)

        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_PORT, JSON_PORT)
        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_LISTEN, '')

        self.mock_server      = MockUPS()
        self.rfs = UserProcessingFacadeServer.UserProcessingRemoteFacadeServer(self.mock_server, self.configurationManager)

    def _generate_two_experiments(self):
        client = Experiment.ExperimentClient("client", {})
        experimentA = Experiment.Experiment(
                'weblab-pld',
                Category.ExperimentCategory('WebLab-PLD experiments'),
                datetime.datetime(2007,1,1),
                datetime.datetime(2008,1,1),
                client
            )
        experimentB = Experiment.Experiment(
                'weblab-fpga',
                Category.ExperimentCategory('WebLab-FPGA experiments'),
                datetime.datetime(2005,1,1),
                datetime.datetime(2006,1,1),
                client
            )
        return experimentA, experimentB

    def _generate_experiments_allowed(self):
        experimentA, experimentB = self._generate_two_experiments()
        exp_allowedA = ExperimentAllowed.ExperimentAllowed( experimentA, 100, 5, True, 'expA::user', 1, 'user')
        exp_allowedB = ExperimentAllowed.ExperimentAllowed( experimentB, 100, 5, True, 'expB::user', 1, 'user')
        return exp_allowedA, exp_allowedB

    @uses_module(RemoteFacadeServer)
    def test_reserve_experiment(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient("http://127.0.0.1:%s/weblab/" % port)

            expected_sess_id = SessionId.SessionId("whatever")
            NUMBER   = 5

            expected_confirmed_reservation = Reservation.ConfirmedReservation("reservation_id", NUMBER, "{}", 'http://www.weblab.deusto.es/...', '')
            expected_experiment_id = self._generate_two_experiments()[0].to_experiment_id()

            self._generate_experiments_allowed()
            self.mock_server.return_values['reserve_experiment'] = expected_confirmed_reservation

            confirmed_reservation = client.reserve_experiment(expected_sess_id, expected_experiment_id, "{}", "{}")

            self.assertEquals(
                    expected_sess_id.id,
                    self.mock_server.arguments['reserve_experiment'][0]
                )
            self.assertEquals(
                    expected_experiment_id.exp_name,
                    self.mock_server.arguments['reserve_experiment'][1].exp_name
                )
            self.assertEquals(
                    expected_experiment_id.cat_name,
                    self.mock_server.arguments['reserve_experiment'][1].cat_name
                )
            self.assertEquals(
                    expected_confirmed_reservation.time,    
                    confirmed_reservation.time
                )
            self.assertEquals(
                    expected_confirmed_reservation.status,
                    confirmed_reservation.status
                )
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_send_command(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient("http://localhost:%s/weblab/" % port)

            expected_sess_id = SessionId.SessionId("whatever")
            expected_request_command  = Command.Command('my request command')
            expected_response_command = Command.Command('my response command')

            self.mock_server.return_values['send_command'] = expected_response_command

            obtained_response_command = client.send_command(expected_sess_id, expected_request_command)

            self.assertEquals(
                    expected_sess_id.id,
                    self.mock_server.arguments['send_command'][0]
                )
            self.assertEquals(
                    expected_request_command.get_command_string(),
                    self.mock_server.arguments['send_command'][1].get_command_string()
                )
            self.assertEquals(
                    expected_response_command.get_command_string(),
                    obtained_response_command.get_command_string()
                )
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_get_experiment_use_by_id(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient("http://localhost:%s/weblab/" % port)

            expected_sess_id = SessionId.SessionId("whatever")
            expected_reservation_id = SessionId.SessionId("foobar")
            expected_alive_result = RunningReservationResult()

            self.mock_server.return_values['get_experiment_use_by_id'] = expected_alive_result


            obtained_result = client.get_experiment_use_by_id(expected_sess_id, expected_reservation_id)
            self.assertEquals(RunningReservationResult(), obtained_result)
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_get_experiment_uses_by_id(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient("http://localhost:%s/weblab/" % port)

            expected_sess_id = SessionId.SessionId("whatever")
            expected_usage = ExperimentUsage(10, time.time(), time.time(), '127.0.0.1', ExperimentId("exp","cat"), 'reser1', CoordAddress('machine','instance','server'))

            command_sent = CommandSent(Command.Command("request"), time.time(), Command.Command("response"), time.time())
            expected_usage.append_command(command_sent)

            loaded_file_sent = LoadedFileSent('content-of-the-file', time.time(), Command.Command("response"), time.time(), 'program')
            expected_usage.append_file(loaded_file_sent)

            expected_finished_result  = FinishedReservationResult(expected_usage)
            expected_alive_result     = RunningReservationResult()
            expected_cancelled_result = CancelledReservationResult()

            self.mock_server.return_values['get_experiment_uses_by_id'] = (expected_finished_result, expected_alive_result, expected_cancelled_result)

            expected_reservations = (SessionId.SessionId('reservation'), SessionId.SessionId('reservation2'), SessionId.SessionId('reservation3') )

            results = client.get_experiment_uses_by_id(expected_sess_id, expected_reservations)

            self.assertEquals( expected_sess_id.id, self.mock_server.arguments['get_experiment_uses_by_id'][0])
            self.assertEquals( expected_reservations, tuple(self.mock_server.arguments['get_experiment_uses_by_id'][1]))


            self.assertEquals(3, len(results))
            self.assertEquals(expected_finished_result.status,  results[0].status)
            self.assertEquals(expected_alive_result.status,     results[1].status)
            self.assertEquals(expected_cancelled_result.status, results[2].status)

            self.assertEquals(expected_usage, results[0].experiment_use)

        finally:
            self.rfs.stop()
    @uses_module(RemoteFacadeServer)
    def test_get_reservation_status(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient("http://localhost:%s/weblab/" % port)

            expected_sess_id = SessionId.SessionId("whatever")
            NUMBER   = 5

            expected_confirmed_reservation = Reservation.ConfirmedReservation("reservation_id", NUMBER, "{}", 'http://www.weblab.deusto.es/...', '')
            self.mock_server.return_values['get_reservation_status'] = expected_confirmed_reservation

            confirmed_reservation = client.get_reservation_status(expected_sess_id)

            self.assertEquals(
                    expected_sess_id.id,
                    self.mock_server.arguments['get_reservation_status'][0]
                )
            self.assertEquals(
                    expected_confirmed_reservation.time,    
                    confirmed_reservation.time
                )
            self.assertEquals(
                    expected_confirmed_reservation.status,
                    confirmed_reservation.status
                )
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_finished_experiment(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient("http://localhost:%s/weblab/" % port)

            expected_sess_id = SessionId.SessionId("whatever")

            self.mock_server.return_values['finished_experiment'] = None

            client.finished_experiment(expected_sess_id)

            self.assertEquals(
                    expected_sess_id.id,
                    self.mock_server.arguments['finished_experiment'][0]
                )
        finally:
            self.rfs.stop()


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(UserProcessingIntegratingRemoteFacadeManagerJSON),
        ))

if __name__ == '__main__':
    unittest.main()

