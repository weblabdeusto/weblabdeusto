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
import sys
import time
import unittest
import datetime

try:
    import ZSI
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

import weblab.configuration_doc as configuration_doc

import voodoo.sessions.session_id as SessionId

import test.unit.configuration as configuration
import voodoo.configuration as ConfigurationManager

import weblab.core.comm.user_manager as UserProcessingFacadeManager
import weblab.comm.codes as RFCodes
import weblab.comm.manager as RFM
import weblab.core.comm.codes as UserProcessingRFCodes
import weblab.core.reservations as Reservation

import weblab.data.dto.experiments as ExperimentAllowed
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as Category
import weblab.data.command as Command
import weblab.data.dto.users as Group

from weblab.data.experiments import WaitingReservationResult, FinishedReservationResult, CancelledReservationResult, ExperimentUsage, LoadedFileSent, CommandSent, ExperimentId

from weblab.data.dto.users import User
from weblab.data.dto.users import Role
from weblab.data.dto.experiments import ExperimentUse
from weblab.data.dto.permissions import Permission, PermissionParameter

import weblab.core.exc as coreExc
import weblab.exc as WebLabErrors
import voodoo.gen.exceptions.exceptions as VoodooErrors

def generate_mock_method(method_name, ordered_arguments):

    def method(self, *args, **kwargs):
        # Reorder the arguments
        final_arguments = list(args)
        ordered_kwargs  = []
        for kwarg in kwargs:
            pos = ordered_arguments.index(kwarg)
            ordered_kwargs[(pos, kwargs[kwarg])]
        ordered_kwargs.sort(lambda ((x1, y1), (x2, y2)) : cmp(x1,x2))
        final_arguments.extend(map(lambda (pos, kwarg) : kwarg, ordered_kwargs))

        # Now store them and throw an exception if required
        self.arguments[method_name] = final_arguments
        if method_name in self.exceptions:
            raise self.exceptions[method_name]
        return self.return_values[method_name]

    method.__name__ = method_name
    return method


class MockUPS(object):

    def __init__(self):
        super(MockUPS, self).__init__()
        self.arguments     = {}
        self.return_values = {}
        self.exceptions    = {}

    logout                    = generate_mock_method('logout',                    ('session_id',))
    list_experiments          = generate_mock_method('list_experiments',          ('session_id',))
    reserve_experiment        = generate_mock_method('reserve_experiment',        ('session_id', 'experiment', 'client_initial_data', 'consumer_data', 'client_address'))
    finished_experiment       = generate_mock_method('finished_experiment',       ('session_id',))
    get_reservation_status    = generate_mock_method('get_reservation_status',    ('session_id',))
    send_file                 = generate_mock_method('send_file',                 ('session_id', 'file_content', 'file_info'))
    send_async_file           = generate_mock_method('send_async_file',           ('session_id', 'file_content', 'file_info'))
    send_command              = generate_mock_method('send_command',              ('session_id', 'command'))
    send_async_command        = generate_mock_method('send_async_command',        ('session_id', 'command'))
    poll                      = generate_mock_method('poll',                      ('session_id',))
    get_user_information      = generate_mock_method('get_user_information',      ('session_id',))
    get_roles                 = generate_mock_method('get_roles',                 ('session_id',))
    get_groups                = generate_mock_method('get_groups',                ('session_id',))
    get_users                 = generate_mock_method('get_users',                 ('session_id',))
    get_experiments           = generate_mock_method('get_experiments',           ('session_id',))
    get_experiment_uses       = generate_mock_method('get_experiment_uses',       ('session_id', 'from_date', 'to_date', 'group_id', 'experiment_id', 'start_row', 'end_row', 'sort_by'))
    get_user_permissions      = generate_mock_method('get_user_permissions',      ('session_id',))
    get_experiment_use_by_id  = generate_mock_method('get_experiment_use_by_id',  ('session_id','reservation_id'))
    get_experiment_uses_by_id = generate_mock_method('get_experiment_uses_by_id', ('session_id','reservation_ids'))

class UserProcessingFacadeManagerZSITestCase(unittest.TestCase):

    def setUp(self):
        self.cfg_manager   = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration)

        self.mock_ups      = MockUPS()

        server_admin_mail = self.cfg_manager.get_value(RFM.SERVER_ADMIN_EMAIL, RFM.DEFAULT_SERVER_ADMIN_EMAIL)
        self.weblab_general_error_message = RFM.UNEXPECTED_ERROR_MESSAGE_TEMPLATE % server_admin_mail

        self.rfm = UserProcessingFacadeManager.UserProcessingRemoteFacadeManagerZSI(
                self.cfg_manager,
                self.mock_ups
            )

    def test_return_logout(self):
        expected_sess_id = SessionId.SessionId("whatever")
        self.mock_ups.return_values['logout'] = expected_sess_id

        self.assertEquals( expected_sess_id.id, self.rfm.logout(expected_sess_id).id )
        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['logout'][0].id )

    def test_return_list_experiments(self):
        expected_sess_id = SessionId.SessionId("whatever")
        experiments_allowed = _generate_experiments_allowed()
        self.mock_ups.return_values['list_experiments'] = experiments_allowed

        self.assertEquals( experiments_allowed, self.rfm.list_experiments(expected_sess_id) )
        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['list_experiments'][0].id )

    def test_return_reserve_experiment(self):
        expected_sess_id = SessionId.SessionId("whatever")
        experimentA, _ = _generate_two_experiments()
        expected_reservation = Reservation.ConfirmedReservation("reservation_id", 100, "{}", 'http://www.weblab.deusto.es/...','')

        self.mock_ups.return_values['reserve_experiment'] = expected_reservation

        self.assertEquals( expected_reservation,
                self.rfm.reserve_experiment( expected_sess_id, experimentA.to_experiment_id(), "{}", "{}"))

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['reserve_experiment'][0].id )
        self.assertEquals( experimentA.name, self.mock_ups.arguments['reserve_experiment'][1].exp_name )
        self.assertEquals( experimentA.category.name, self.mock_ups.arguments['reserve_experiment'][1].cat_name )
        self.assertEquals( "{}", self.mock_ups.arguments['reserve_experiment'][2] )

    def test_return_finished_experiment(self):
        expected_sess_id = SessionId.SessionId("whatever")

        self.mock_ups.return_values['finished_experiment'] = None

        self.rfm.finished_experiment(expected_sess_id)

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['finished_experiment'][0].id )

    def test_return_get_reservation_status(self):
        expected_sess_id = SessionId.SessionId("whatever")

        expected_reservation = Reservation.ConfirmedReservation("reservation_id", 100, "{}", 'http://www.weblab.deusto.es/...','')

        self.mock_ups.return_values['get_reservation_status'] = expected_reservation


        reservation = self.rfm.get_reservation_status(expected_sess_id)

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['get_reservation_status'][0].id )
        self.assertEquals( expected_reservation.status, reservation.status )
        self.assertEquals( expected_reservation.time, reservation.time )

    def test_return_send_file(self):
        expected_sess_id      = SessionId.SessionId("whatever")
        expected_file_content = "<content of the file>"

        self.mock_ups.return_values['send_file']        = None

        self.rfm.send_file( expected_sess_id, expected_file_content, 'program' )

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['send_file'][0].id )
        self.assertEquals( expected_file_content, self.mock_ups.arguments['send_file'][1] )

    def test_return_send_command(self):
        expected_sess_id = SessionId.SessionId("whatever")
        expected_command = Command.Command("ChangeSwitch on 9")

        self.mock_ups.return_values['send_command'] = None

        self.rfm.send_command( expected_sess_id, expected_command )

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['send_command'][0].id )
        self.assertEquals( expected_command.get_command_string(), self.mock_ups.arguments['send_command'][1].get_command_string() )

    def test_return_poll(self):
        expected_sess_id = SessionId.SessionId("whatever")

        self.mock_ups.return_values['poll'] = None

        self.rfm.poll(expected_sess_id)

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['poll'][0].id )

    def test_return_get_experiment_use_by_id(self):
        expected_sess_id = SessionId.SessionId("whatever")

        expected_alive_result = WaitingReservationResult()
        self.mock_ups.return_values['get_experiment_use_by_id'] = expected_alive_result

        alive_result = self.rfm.get_experiment_use_by_id(expected_sess_id, SessionId.SessionId('reservation'))
        self.assertEquals(expected_alive_result.status, alive_result.status)

    def test_return_get_experiment_uses_by_id(self):
        expected_sess_id = SessionId.SessionId("whatever")

        expected_usage = ExperimentUsage(10, time.time(), time.time(), '127.0.0.1', ExperimentId("exp","cat"))

        command_sent = CommandSent(Command.Command("request"), time.time(), Command.Command("response"), time.time())
        expected_usage.append_command(command_sent)

        loaded_file_sent = LoadedFileSent('content-of-the-file', time.time(), Command.Command("response"), time.time(), 'program')
        expected_usage.append_file(loaded_file_sent)

        expected_finished_result  = FinishedReservationResult(expected_usage)
        expected_alive_result     = WaitingReservationResult()
        expected_cancelled_result = CancelledReservationResult()

        self.mock_ups.return_values['get_experiment_uses_by_id'] = (expected_finished_result, expected_alive_result, expected_cancelled_result)

        results = self.rfm.get_experiment_uses_by_id(expected_sess_id, (SessionId.SessionId('reservation'), SessionId.SessionId('reservation2'), SessionId.SessionId('reservation3') ))

        self.assertEquals(3, len(results))
        self.assertEquals(expected_finished_result.status,  results[0].status)
        self.assertEquals(expected_alive_result.status,     results[1].status)
        self.assertEquals(expected_cancelled_result.status, results[2].status)

        self.assertEquals(expected_usage, expected_finished_result.experiment_use)


    def test_return_get_user_information(self):
        expected_sess_id = SessionId.SessionId("whatever")

        expected_user_information = User( 'porduna', 'Pablo Orduna', 'weblab@deusto.es', Role("student"))

        self.mock_ups.return_values['get_user_information'] = expected_user_information

        user_information = self.rfm.get_user_information(expected_sess_id)

        self.assertEquals( expected_sess_id.id, self.mock_ups.arguments['get_user_information'][0].id )
        self.assertEquals( expected_user_information.login, user_information.login )
        self.assertEquals( expected_user_information.full_name, user_information.full_name )
        self.assertEquals( expected_user_information.email, user_information.email )
        self.assertEquals( expected_user_information.role.name, user_information.role.name)

    def _generate_real_mock_raising(self, method, exception, message):
        self.mock_ups.exceptions[method] = exception(message)


    def _test_exception(self, method, args, exc_to_raise, exc_message, expected_code, expected_exc_message):
        self._generate_real_mock_raising(method, exc_to_raise, exc_message )

        try:
            getattr(self.rfm, method)(*args)
            self.fail('exception expected')
        except ZSI.Fault as e:
            self.assertEquals(expected_code, e.code)
            self.assertEquals(expected_exc_message, e.string)

    def _test_general_exceptions(self, method, *args):
        MESSAGE = "The exception message"

        # Production mode: A general error message is received
        self.cfg_manager._set_value(configuration_doc.DEBUG_MODE, False)

        self._test_exception(method, args,
                        coreExc.WebLabCoreError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,
                        WebLabErrors.WebLabError, MESSAGE,
                        'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,
                        VoodooErrors.GeneratorError, MESSAGE,
                        'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,
                        Exception, MESSAGE,
                        'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        # Debug mode: The error message is received
        self.cfg_manager._set_value(configuration_doc.DEBUG_MODE, True)

        self._test_exception(method, args,
                        coreExc.WebLabCoreError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.UPS_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,
                        WebLabErrors.WebLabError, MESSAGE,
                        'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,
                        VoodooErrors.GeneratorError, MESSAGE,
                        'ZSI:' + RFCodes.VOODOO_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,
                        Exception, MESSAGE,
                        'ZSI:' + RFCodes.PYTHON_GENERAL_EXCEPTION_CODE, MESSAGE)

    def test_exception_logout(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")

        self._test_exception('logout', (expected_sess_id,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('logout', expected_sess_id)


    def test_exception_list_experiments(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")

        self._test_exception('list_experiments', (expected_sess_id,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('list_experiments', expected_sess_id)


    def test_exception_reserve_experiment(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")
        experimentA, _ = _generate_two_experiments()

        self._test_exception('reserve_experiment', (expected_sess_id, experimentA.to_experiment_id(), "{}", "{}"),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_exception('reserve_experiment', (expected_sess_id, experimentA.to_experiment_id(), "{}", "{}"),
                        coreExc.UnknownExperimentIdError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_UNKNOWN_EXPERIMENT_ID_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('reserve_experiment', expected_sess_id, experimentA.to_experiment_id(), "{}", "{}")

    def test_exception_finished_experiment(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")

        self._test_exception('finished_experiment', (expected_sess_id,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_exception('finished_experiment', (expected_sess_id,),
                        coreExc.NoCurrentReservationError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('finished_experiment', expected_sess_id)


    def test_exception_get_reservation_status(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")

        self._test_exception('get_reservation_status', (expected_sess_id,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_exception('get_reservation_status', (expected_sess_id,),
                        coreExc.NoCurrentReservationError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('get_reservation_status', expected_sess_id)

    def test_exception_send_file(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")
        FILE_CONTENT = 'whatever'

        self._test_exception('send_file', (expected_sess_id, FILE_CONTENT, 'program',),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_exception('send_file', (expected_sess_id, FILE_CONTENT, 'program',),
                        coreExc.NoCurrentReservationError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('send_file', expected_sess_id, FILE_CONTENT, 'program')

    def test_exception_send_command(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")
        COMMAND = Command.Command('whatever')

        self._test_exception('send_command', (expected_sess_id, COMMAND,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_exception('send_command', (expected_sess_id, COMMAND,),
                        coreExc.NoCurrentReservationError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('send_command', expected_sess_id, COMMAND)

    def test_exception_poll(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")

        self._test_exception('poll', (expected_sess_id,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_exception('poll', (expected_sess_id,),
                        coreExc.NoCurrentReservationError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('poll', expected_sess_id)


    def test_exception_get_user_information(self):
        MESSAGE = "The exception message"
        expected_sess_id  = SessionId.SessionId("whatever")

        self._test_exception('get_user_information', (expected_sess_id,),
                        coreExc.SessionNotFoundError, MESSAGE,
                        'ZSI:' + UserProcessingRFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE, MESSAGE)

        self._test_general_exceptions('get_user_information', expected_sess_id)



class UserProcessingFacadeManagerJSONTestCase(unittest.TestCase):

    def setUp(self):

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration)

        self.mock_ups = MockUPS()

        server_admin_mail = self.cfg_manager.get_value(RFM.SERVER_ADMIN_EMAIL, RFM.DEFAULT_SERVER_ADMIN_EMAIL)
        self.weblab_general_error_message = RFM.UNEXPECTED_ERROR_MESSAGE_TEMPLATE % server_admin_mail

        self.rfm = UserProcessingFacadeManager.UserProcessingRemoteFacadeManagerJSON(
                self.cfg_manager,
                self.mock_ups
            )

    def _generate_groups(self):
        group1 = Group.Group("group 1")
        group11 = Group.Group("group 1.1")
        group12 = Group.Group("group 1.2")
        group2 = Group.Group("group 2")
        group1.add_child(group11)
        group1.add_child(group12)
        return group1, group2

    def _generate_users(self):
        user1 = User("Login", "FullName", "Email@deusto.es", Role("student"))
        user2 = User("Login2", "FullName2", "Email2@deusto.es", Role("administrator"))
        return user1, user2

    def _generate_roles(self):
        role1 = Role("student")
        role2 = Role("professor")
        role3 = Role("administrator")
        return role1, role2, role3

    def _generate_experiments(self):
        experimentA = Experiment.Experiment(
                'weblab-pld',
                Category.ExperimentCategory('WebLab-PLD experiments'),
                'start_date',
                'end_date'
            )
        experimentB = Experiment.Experiment(
                'weblab-pld',
                Category.ExperimentCategory('WebLab-PLD experiments'),
                'start_date',
                'end_date'
            )
        return experimentA, experimentB



    def test_return_logout(self):
        expected_sess_id = {'id': "whatever"}

        self.mock_ups.return_values['logout'] = expected_sess_id

        self.assertEquals( expected_sess_id['id'], self.rfm.logout(expected_sess_id)['id'] )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['logout'][0].id )

    def test_return_list_experiments(self):
        expected_sess_id = {'id': "whatever"}
        experiments_allowed = _generate_experiments_allowed()

        self.mock_ups.return_values['list_experiments'] = experiments_allowed

        self.assertEquals( experiments_allowed, self.rfm.list_experiments(expected_sess_id) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['list_experiments'][0].id )

    def test_return_reserve_experiment(self):
        expected_sess_id = {'id': "whatever"}
        experimentA, _ = _generate_two_experiments()
        expected_reservation = Reservation.ConfirmedReservation("reservation_id", 100, "{}", 'http://www.weblab.deusto.es/...','')

        self.mock_ups.return_values['reserve_experiment'] = expected_reservation

        self.assertEquals( expected_reservation,
                self.rfm.reserve_experiment( expected_sess_id, experimentA.to_experiment_id().to_dict(), "{}", "{}"))

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['reserve_experiment'][0].id )
        self.assertEquals( experimentA.name, self.mock_ups.arguments['reserve_experiment'][1].exp_name )
        self.assertEquals( experimentA.category.name, self.mock_ups.arguments['reserve_experiment'][1].cat_name )

    def test_return_finished_experiment(self):
        expected_sess_id = {'id': "whatever"}

        self.mock_ups.return_values['finished_experiment'] = None

        self.rfm.finished_experiment(expected_sess_id)

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['finished_experiment'][0].id)

    def test_return_get_reservation_status(self):
        expected_sess_id = {'id': "whatever"}

        expected_reservation = Reservation.ConfirmedReservation("reservation_id", 100, "{}", 'http://www.weblab.deusto.es/...','')

        self.mock_ups.return_values['get_reservation_status'] = expected_reservation


        reservation = self.rfm.get_reservation_status(expected_sess_id)

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_reservation_status'][0].id )
        self.assertEquals( expected_reservation.status, reservation.status )
        self.assertEquals( expected_reservation.time, reservation.time )

    def test_return_send_file(self):
        expected_sess_id      = {'id': "whatever"}
        expected_file_content = "<content of the file>"

        self.mock_ups.return_values['send_file']        = None

        self.rfm.send_file( expected_sess_id, expected_file_content, 'program' )

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['send_file'][0].id )
        self.assertEquals( expected_file_content, self.mock_ups.arguments['send_file'][1] )

    def test_return_send_command(self):
        expected_sess_id = {'id': "whatever"}
        expected_command = Command.Command("ChangeSwitch on 9")

        self.mock_ups.return_values['send_command'] = None

        self.rfm.send_command( expected_sess_id, expected_command.to_dict() )

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['send_command'][0].id )
        self.assertEquals( expected_command.get_command_string(), self.mock_ups.arguments['send_command'][1].get_command_string() )

    def test_return_poll(self):
        expected_sess_id = {'id': "whatever"}

        self.mock_ups.return_values['poll'] = None

        self.rfm.poll(expected_sess_id)

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['poll'][0].id )

    def test_return_get_user_information(self):
        expected_sess_id = {'id': "whatever"}

        expected_user_information = User( 'porduna', 'Pablo Orduna', 'weblab@deusto.es', Role("student") )

        self.mock_ups.return_values['get_user_information'] = expected_user_information

        user_information = self.rfm.get_user_information(expected_sess_id)

        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_user_information'][0].id )
        self.assertEquals( expected_user_information.login, user_information.login )
        self.assertEquals( expected_user_information.full_name, user_information.full_name )
        self.assertEquals( expected_user_information.email, user_information.email )
        self.assertEquals( expected_user_information.role.name, user_information.role.name )

    def test_return_get_groups(self):
        expected_sess_id = {'id' : 'whatever'}
        groups = self._generate_groups()

        self.mock_ups.return_values['get_groups'] = groups

        self.assertEquals( groups, self.rfm.get_groups(expected_sess_id) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_groups'][0].id )

    def test_return_get_users(self):
        expected_sess_id = {'id' : "whatever"}
        users = self._generate_users()

        self.mock_ups.return_values['get_users'] = users

        self.assertEquals( users, self.rfm.get_users(expected_sess_id) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_users'][0].id )


    def test_return_get_roles(self):
        expected_sess_id = {'id' : "whatever"}
        roles = self._generate_roles()

        self.mock_ups.return_values['get_roles'] = roles

        self.assertEquals( roles, self.rfm.get_roles(expected_sess_id) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_roles'][0].id )


    def test_return_get_experiments(self):
        expected_sess_id = {'id' : "whatever"}
        experiments = self._generate_experiments()

        self.mock_ups.return_values['get_experiments'] = experiments

        self.assertEquals( experiments, self.rfm.get_experiments(expected_sess_id) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_experiments'][0].id )

    def test_return_get_experiment_uses(self):
        expected_sess_id = {'id' : "whatever"}
        experiment_uses = _generate_experiment_uses()

        self.mock_ups.return_values['get_experiment_uses'] = experiment_uses

        self.assertEquals( experiment_uses, self.rfm.get_experiment_uses(expected_sess_id, None, None, None, None, None, None, None) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_experiment_uses'][0].id )
        self.assertEquals( None, self.mock_ups.arguments['get_experiment_uses'][1] )
        self.assertEquals( None, self.mock_ups.arguments['get_experiment_uses'][2] )
        self.assertEquals( None, self.mock_ups.arguments['get_experiment_uses'][3] )
        self.assertEquals( None, self.mock_ups.arguments['get_experiment_uses'][4] )

    def test_return_get_user_permissions(self):
        expected_sess_id = {'id' : "whatever"}
        permissions = _generate_permissions()

        self.mock_ups.return_values['get_user_permissions'] = permissions

        self.assertEquals( permissions, self.rfm.get_user_permissions(expected_sess_id) )
        self.assertEquals( expected_sess_id['id'], self.mock_ups.arguments['get_user_permissions'][0].id )

    def _generate_real_mock_raising(self, method, exception, message):
        self.mock_ups.exceptions[method] = exception(message)


    def _test_exception(self, method, args, exc_to_raise, exc_message, expected_code, expected_exc_message):
        self._generate_real_mock_raising(method, exc_to_raise, exc_message )

        try:
            getattr(self.rfm, method)(*args)
            self.fail('exception expected')
        except ZSI.Fault as e:
            self.assertEquals(expected_code, e.code)
            self.assertEquals(expected_exc_message, e.string)

    def _test_general_exceptions(self, method, *args):
        MESSAGE = "The exception message"

        # Production mode: A general error message is received
        self.cfg_manager._set_value(configuration_doc.DEBUG_MODE, False)

        self._test_exception(method, args,
                        coreExc.WebLabCoreError, MESSAGE,
                        'JSON:' + UserProcessingRFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,
                        WebLabErrors.WebLabError, MESSAGE,
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,
                        VoodooErrors.GeneratorError, MESSAGE,
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,
                        Exception, MESSAGE,
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        # Debug mode: The error message is received
        self.cfg_manager._set_value(configuration_doc.DEBUG_MODE, True)

        self._test_exception(method, args,
                        coreExc.WebLabCoreError, MESSAGE,
                        'JSON:' + UserProcessingRFCodes.UPS_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,
                        WebLabErrors.WebLabError, MESSAGE,
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,
                        VoodooErrors.GeneratorError, MESSAGE,
                        'JSON:' + RFCodes.VOODOO_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,
                        Exception, MESSAGE,
                        'JSON:' + RFCodes.PYTHON_GENERAL_EXCEPTION_CODE, MESSAGE)


def _generate_two_experiments():
    experimentA = Experiment.Experiment(
            'weblab-pld',
            Category.ExperimentCategory('WebLab-PLD experiments'),
            'start_date',
            'end_date'
        )
    experimentB = Experiment.Experiment(
            'weblab-pld',
            Category.ExperimentCategory('WebLab-PLD experiments'),
            'start_date',
            'end_date'
        )
    return experimentA, experimentB


def _generate_experiments_allowed():
    experimentA, experimentB = _generate_two_experiments()
    exp_allowedA = ExperimentAllowed.ExperimentAllowed( experimentA, 100, 5, True, 'expA::user', 1, 'user')
    exp_allowedB = ExperimentAllowed.ExperimentAllowed( experimentB, 100, 5, True, 'expB::user', 1, 'user')
    return exp_allowedA, exp_allowedB


def _generate_groups():
    group1 = Group.Group("group 1")
    group11 = Group.Group("group 1.1")
    group12 = Group.Group("group 1.2")
    group2 = Group.Group("group 2")
    group1.add_child(group11)
    group1.add_child(group12)
    return group1, group2


def _generate_experiment_uses():
    exp1, exp2 = _generate_two_experiments()
    use1 = ExperimentUse(
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow(),
        exp1,
        User(
            "jaime.irurzun",
            "Jaime Irurzun",
            "jaime.irurzun@opendeusto.es",
            Role("student")),
        "unknown")
    use2 = ExperimentUse(
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow(),
        exp2,
        User(
            "pablo.orduna",
            "Pablo Orduna",
            "pablo.ordunya@opendeusto.es",
            Role("student")),
        "unknown")
    return (use1, use2), 2


def _generate_permissions():
    p1 = Permission("experiment_allowed")
    p1.add_parameter(PermissionParameter("experiment_name", "string", "ud-fpga"))
    p1.add_parameter(PermissionParameter("experiment_category", "string", "FPGA experiments"))
    p1.add_parameter(PermissionParameter("time_allowed", "float", "300"))
    p2 = Permission("admin_panel_access")
    p2.add_parameter(PermissionParameter("full_privileges", "bool", "300"))
    return p1, p2


def suite():
    test_cases = [ unittest.makeSuite(UserProcessingFacadeManagerJSONTestCase) ]
    if ZSI_AVAILABLE:
        test_cases.append(unittest.makeSuite(UserProcessingFacadeManagerZSITestCase))
    else:
        print >> sys.stderr, "Optional module 'ZSI' not available. Tests in UserProcessingFacadeManagerZSITestCase skipped."

    return unittest.TestSuite(test_cases)

if __name__ == '__main__':
    unittest.main()

