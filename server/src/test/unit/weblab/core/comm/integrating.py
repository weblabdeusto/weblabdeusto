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
import sys
import unittest

try:
    import ZSI
    from weblab.core.comm.generated.weblabdeusto_client import weblabdeustoSOAP as UserProcessingWebLabDeustoSOAP
except ImportError:
    pass

import datetime

import voodoo.sessions.session_id as SessionId
import weblab.data.dto.experiments as ExperimentAllowed
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as Category

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

from test.unit.weblab.core.comm.user_manager import MockUPS

class UserProcessingIntegratingRemoteFacadeManager(unittest.TestCase):
    if UserProcessingFacadeServer.ZSI_AVAILABLE:
        def setUp(self):
            self.configurationManager = ConfigurationManager.ConfigurationManager()
            self.configurationManager.append_module(configuration)

            self.configurationManager._set_value(RemoteFacadeServer.RFS_TIMEOUT_NAME, 0.001)

            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_ZSI_PORT, 10223)
            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_ZSI_SERVICE_NAME, '/weblab/soap/')
            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_ZSI_LISTEN, '')

            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_PORT, 10224)
            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_LISTEN, '')

            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_XMLRPC_PORT, 10225)
            self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_XMLRPC_LISTEN, '')


            self.mock_server      = MockUPS()
            self.rfs = UserProcessingFacadeServer.UserProcessingRemoteFacadeServer(self.mock_server, self.configurationManager)

        def _generate_two_experiments(self):
            experimentA = Experiment.Experiment(
                    'weblab-pld',
                    Category.ExperimentCategory('WebLab-PLD experiments'),
                    datetime.datetime(2007,1,1),
                    datetime.datetime(2008,1,1)
                )
            experimentB = Experiment.Experiment(
                    'weblab-fpga',
                    Category.ExperimentCategory('WebLab-FPGA experiments'),
                    datetime.datetime(2005,1,1),
                    datetime.datetime(2006,1,1)
                )
            return experimentA, experimentB

        def _generate_experiments_allowed(self):
            experimentA, experimentB = self._generate_two_experiments()
            exp_allowedA = ExperimentAllowed.ExperimentAllowed( experimentA, 100, 5, True)
            exp_allowedB = ExperimentAllowed.ExperimentAllowed( experimentB, 100, 5, True)
            return exp_allowedA, exp_allowedB

        @uses_module(RemoteFacadeServer)
        def test_logout(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14124)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14124/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")
                MESSAGE  = 'my message'

                self.mock_server.return_values['logout'] = expected_sess_id

                wds.logout(expected_sess_id)

                self.assertEquals(
                        expected_sess_id.id,
                        self.mock_server.arguments['logout'][0]
                    )

                self.mock_server.exceptions['logout'] = coreExc.SessionNotFoundException(MESSAGE)

                try:
                    wds.logout(expected_sess_id)
                    self.fail('exception expected')
                except ZSI.FaultException as e:
                    self.assertEquals(
                        UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE,
                        e.fault.code[1]
                    )
                    self.assertEquals(
                        MESSAGE,
                        e.fault.string
                    )
            finally:
                self.rfs.stop()

        @uses_module(RemoteFacadeServer)
        def test_list_experiments(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14125)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14125/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")

                expected_experiments = self._generate_experiments_allowed()
                self.mock_server.return_values['list_experiments'] = expected_experiments

                experiments = wds.list_experiments(expected_sess_id)

                self.assertEquals(
                        expected_sess_id.id,
                        self.mock_server.arguments['list_experiments'][0]
                    )

                self.assertEquals(
                        len(expected_experiments),
                        len(experiments)
                    )

                self.assertEquals(
                        expected_experiments[0].experiment.name,
                        experiments[0].experiment.name
                    )

                self.assertEquals(
                        expected_experiments[0].experiment.category.name,
                        experiments[0].experiment.category.name
                    )
            finally:
                self.rfs.stop()

        @uses_module(RemoteFacadeServer)
        def test_reserve_experiment(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14126)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14126/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")
                NUMBER   = 5

                expected_confirmed_reservation = Reservation.ConfirmedReservation("reservation_id", NUMBER, "{}")
                expected_experiment_id = self._generate_two_experiments()[0].to_experiment_id()

                self._generate_experiments_allowed()
                self.mock_server.return_values['reserve_experiment'] = expected_confirmed_reservation

                confirmed_reservation = wds.reserve_experiment(expected_sess_id, expected_experiment_id, "{}", "{}")

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
        def test_finished_experiment(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14127)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14127/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")

                self.mock_server.return_values['finished_experiment'] = None

                wds.finished_experiment(expected_sess_id)

                self.assertEquals(
                        expected_sess_id.id,
                        self.mock_server.arguments['finished_experiment'][0]
                    )
            finally:
                self.rfs.stop()

        @uses_module(RemoteFacadeServer)
        def test_get_reservation_status(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14128)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14128/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")
                NUMBER   = 5

                expected_confirmed_reservation = Reservation.ConfirmedReservation("reservation_id", NUMBER, "{}")
                self.mock_server.return_values['get_reservation_status'] = expected_confirmed_reservation

                confirmed_reservation = wds.get_reservation_status(expected_sess_id)

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
        def test_send_file(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14129)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14129/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")
                expected_content = 'my file'
                expected_result  = 'hello there'
                file_info        = 'program'

                self.mock_server.return_values['send_file'   ]     = Command.Command(expected_result)

                result = wds.send_file(expected_sess_id, expected_content, file_info)

                self.assertEquals(
                        expected_sess_id.id,
                        self.mock_server.arguments['send_file'][0]
                    )
                self.assertEquals(
                        expected_content,
                        self.mock_server.arguments['send_file'][1]
                    )
                self.assertEquals(
                        expected_result,
                        result.commandstring
                    )
            finally:
                self.rfs.stop()

        @uses_module(RemoteFacadeServer)
        def test_send_command(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14130)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14130/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")
                expected_command = Command.Command('my command')

                self.mock_server.return_values['send_command'] = expected_command

                wds.send_command(expected_sess_id, expected_command)

                self.assertEquals(
                        expected_sess_id.id,
                        self.mock_server.arguments['send_command'][0]
                    )
                self.assertEquals(
                        expected_command.get_command_string(),
                        self.mock_server.arguments['send_command'][1].get_command_string()
                    )
            finally:
                self.rfs.stop()
        
        @uses_module(RemoteFacadeServer)
        def test_get_user_information(self):
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, 14131)
            self.rfs.start()
            try:
                wds = UserProcessingWebLabDeustoSOAP("http://localhost:14131/weblab/soap/")

                expected_sess_id = SessionId.SessionId("whatever")

                expected_user_information = User(
                        'porduna', 
                        'Pablo Orduna', 
                        'weblab@deusto.es',
                        Role("student")
                    )
                self.mock_server.return_values['get_user_information'] = expected_user_information

                user_information = wds.get_user_information(expected_sess_id)

                self.assertEquals(
                        expected_sess_id.id,
                        self.mock_server.arguments['get_user_information'][0]
                    )
                self.assertEquals(
                        expected_user_information.full_name,    
                        user_information.full_name
                    )
                self.assertEquals(
                        expected_user_information.login,    
                        user_information.login
                    )
                self.assertEquals(
                        expected_user_information.email,
                        user_information.email
                    )
                self.assertEquals(
                        expected_user_information.role.name,
                        user_information.role.name
                    )
            finally:
                self.rfs.stop()
    else:
        print >> sys.stderr, "Optional library 'ZSI' not available. Tests in weblab.core.comm.Integrating skipped"

def suite():
    return unittest.makeSuite(UserProcessingIntegratingRemoteFacadeManager)

if __name__ == '__main__':
    unittest.main()

