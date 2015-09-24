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
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import unittest
import time
import datetime

import mocker

from voodoo.gen import CoordAddress
import voodoo.sessions.session_id as SessionId
from   test.util.module_disposer import case_uses_module

import weblab.core.user_processor as UserProcessor
from weblab.core.reservation_processor import ReservationProcessor, EXPERIMENT_POLL_TIME
import weblab.core.reservations as Reservation
import weblab.core.coordinator.confirmer as Confirmer
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.data.server_type as ServerType

from weblab.core.coordinator.gateway import create as coordinator_create, SQLALCHEMY

import weblab.data.command as Command
import weblab.data.dto.users as Group
from weblab.data.experiments import ExperimentInstanceId, ExperimentId
import weblab.data.dto.experiments as Category
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as ExperimentAllowed
import weblab.data.dto.experiments as ExperimentUse
import weblab.data.dto.users as User
import weblab.data.dto.users as Role

from weblab.data import ValidDatabaseSessionId

from weblab.core.coordinator.resource import Resource
from weblab.core.coordinator.config_parser import COORDINATOR_LABORATORY_SERVERS

import weblab.core.exc as coreExc
import weblab.lab.exc as LaboratoryErrors

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

laboratory_coordaddr = CoordAddress.translate(
        "server:laboratoryserver@labmachine"
    )

@case_uses_module(Confirmer)
class ReservationProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.mocker  = mocker.Mocker()
        self.lab_mock = self.mocker.mock()

        self.locator = FakeLocator( lab = self.lab_mock )
        self.db      = FakeDatabase()

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value(COORDINATOR_LABORATORY_SERVERS, {
            'server:laboratoryserver@labmachine' : {
                'inst|ud-dummy|Dummy experiments' : 'res_inst@res_type'
            }
        })

        self.commands_store = TemporalInformationStore.CommandsTemporalInformationStore()

        self.coordinator = coordinator_create(SQLALCHEMY, self.locator, self.cfg_manager)
        self.coordinator._clean()
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), Resource("res_type", "res_inst"))

        self.user_processor = UserProcessor.UserProcessor(
                    self.locator,
                    {
                        'db_session_id' : ValidDatabaseSessionId('my_db_session_id')
                    },
                    self.cfg_manager,
                    self.coordinator,
                    self.db,
                    self.commands_store
                )

    def create_reservation_processor(self, faking_response = False):
        if faking_response:
            self._fake_simple_lab_response()

        status = self.user_processor.reserve_experiment( ExperimentId('ud-dummy', 'Dummy experiments'), "{}", "{}", "127.0.0.1", 'uuid')
        self.reservation_processor = ReservationProcessor(
                    self.cfg_manager,
                    SessionId.SessionId(status.reservation_id.split(';')[0]),
                    {
'session_polling'    : (time.time(), ReservationProcessor.EXPIRATION_TIME_NOT_SET),
                        'latest_timestamp'   : 0,
                        'experiment_id'      : ExperimentId('ud-dummy', 'Dummy experiments'),
                        'creator_session_id' : '',
                        'reservation_id'     : SessionId.SessionId(status.reservation_id.split(';')[0]),
                    },
                    self.coordinator,
                    self.locator,
                    self.commands_store
                )

    def tearDown(self):
        self.coordinator.stop()

    def test_get_info(self):
        self.create_reservation_processor(True)

        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        reservation_info = self.reservation_processor.get_info()
        self.assertEquals('ud-dummy',          reservation_info.exp_name)
        self.assertEquals('Dummy experiments', reservation_info.cat_name)

    def test_is_polling(self):
        self.create_reservation_processor(True)

        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.assertTrue( self.reservation_processor.is_polling() )

        self.reservation_processor.finish()

        self.assertFalse( self.reservation_processor.is_polling() )

    def test_is_expired_didnt_expire(self):
        self.create_reservation_processor(True)
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.assertFalse( self.reservation_processor.is_expired() )

        self.reservation_processor.finish()

        self.assertTrue( self.reservation_processor.is_expired() )

    def test_is_expired_expired_without_expiration_time_set(self):
        time_mock = self.mocker.mock()
        time_mock.time()

        poll_time = self.cfg_manager.get_value(EXPERIMENT_POLL_TIME)
        added = poll_time + 5

        self.mocker.result(time.time() + added)
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.time_module = time_mock

        self.assertTrue( self.reservation_processor.is_expired() )

    def test_is_expired_expired_due_to_expiration_time(self):
        self._return_reserved()

        poll_time = self.cfg_manager.get_value(EXPERIMENT_POLL_TIME)
        added = poll_time - 5 # for example
        self.db.experiments_allowed[0].time_allowed = poll_time - 10
        self.assertTrue( added > 0 )

        time_mock = self.mocker.mock()
        time_mock.time()
        self.mocker.result(time.time() + added)

        self.mocker.replay()

        #
        # Reserve the experiment
        self.create_reservation_processor()

        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        reservation_status = self.reservation_processor.get_status()

        self.assertTrue( isinstance(reservation_status, Reservation.ConfirmedReservation) )

        self.reservation_processor.time_module = time_mock

        self.assertTrue( self.reservation_processor.is_expired() )

    def test_finished_experiment_ok(self):
        self.create_reservation_processor(True)
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())
        self.reservation_processor.finish()

    def test_finished_experiment_coordinator_error(self):
        self.create_reservation_processor(True)
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        # Force the coordinator to fail when invoking finish_reservation
        self.coordinator.finish_reservation = lambda *args: 10 / 0

        self.assertRaises(
                coreExc.FailedToFreeReservationError,
                self.reservation_processor.finish)

    def test_send_async_file_ok(self):
        file_content = "SAMPLE CONTENT"
        lab_response  = Command.Command("LAB RESPONSE")
        file_info    = 'program'
        self._return_reserved()

        self.lab_mock.send_async_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.result(lab_response)

        self.mocker.replay()

        self.create_reservation_processor()

        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())
        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        response = self.reservation_processor.send_async_file(file_content, file_info)

        self.assertEquals(lab_response, response)

        self.assertFalse( self.reservation_processor.is_expired() )

        self.reservation_processor.finish()

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_file_ok(self):
        file_content = "SAMPLE CONTENT"
        lab_response  = Command.Command("LAB RESPONSE")
        file_info    = 'program'
        self._return_reserved()

        self.lab_mock.send_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.result(lab_response)

        self.mocker.replay()

        self.create_reservation_processor()

        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())
        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        response = self.reservation_processor.send_file(file_content, file_info)

        self.assertEquals(lab_response, response)

        self.assertFalse( self.reservation_processor.is_expired() )

        self.reservation_processor.finish()

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_file_session_not_found_in_lab(self):
        self._return_reserved()

        file_content = "SAMPLE CONTENT"
        file_info    = "program"
        self.lab_mock.send_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.throw(
                LaboratoryErrors.SessionNotFoundInLaboratoryServerError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.NoCurrentReservationError,
                self.reservation_processor.send_file,
                file_content,
                file_info
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_async_file_session_not_found_in_lab(self):
        self._return_reserved()

        file_content = "SAMPLE CONTENT"
        file_info    = "program"
        self.lab_mock.send_async_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.throw(
                LaboratoryErrors.SessionNotFoundInLaboratoryServerError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.NoCurrentReservationError,
                self.reservation_processor.send_async_file,
                file_content,
                file_info
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_async_file_failed_to_send(self):
        self._return_reserved()

        file_content = "SAMPLE CONTENT"
        file_info    = "program"
        self.lab_mock.send_async_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.throw(
                LaboratoryErrors.FailedToInteractError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.FailedToInteractError,
                self.reservation_processor.send_async_file,
                file_content,
                file_info
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_file_failed_to_send(self):
        self._return_reserved()

        file_content = "SAMPLE CONTENT"
        file_info    = "program"
        self.lab_mock.send_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.throw(
                LaboratoryErrors.FailedToInteractError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.FailedToInteractError,
                self.reservation_processor.send_file,
                file_content,
                file_info
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_async_command_ok(self):
        self._return_reserved()

        command = Command.Command("Your command")
        lab_response  = Command.Command("LAB RESPONSE")
        self.lab_mock.send_async_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.result(lab_response)

        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        response = self.reservation_processor.send_async_command(command)

        self.assertEquals(lab_response, response)

        self.assertFalse( self.reservation_processor.is_expired() )

        self.reservation_processor.finish()

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )



    def test_send_command_ok(self):
        self._return_reserved()

        command = Command.Command("Your command")
        lab_response  = Command.Command("LAB RESPONSE")
        self.lab_mock.send_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.result(lab_response)

        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        response = self.reservation_processor.send_command(command)

        self.assertEquals(lab_response, response)

        self.assertFalse( self.reservation_processor.is_expired() )

        self.reservation_processor.finish()

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )


    def test_send_command_session_not_found_in_lab(self):
        self._return_reserved()

        command = Command.Command("Your command")
        self.lab_mock.send_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.throw(
                LaboratoryErrors.SessionNotFoundInLaboratoryServerError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.NoCurrentReservationError,
                self.reservation_processor.send_command,
                command
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )


    def test_send_async_command_session_not_found_in_lab(self):
        self._return_reserved()

        command = Command.Command("Your command")
        self.lab_mock.send_async_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.throw(
                LaboratoryErrors.SessionNotFoundInLaboratoryServerError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.NoCurrentReservationError,
                self.reservation_processor.send_async_command,
                command
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_async_command_failed_to_send(self):
        self._return_reserved()

        command = Command.Command("Your command")
        self.lab_mock.send_async_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.throw(
                LaboratoryErrors.FailedToInteractError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.FailedToInteractError,
                self.reservation_processor.send_async_command,
                command
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def test_send_command_failed_to_send(self):
        self._return_reserved()

        command = Command.Command("Your command")
        self.lab_mock.send_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.throw(
                LaboratoryErrors.FailedToInteractError("problem@laboratory")
            )
        self.mocker.replay()

        self.create_reservation_processor()
        self.coordinator.confirmer._confirm_handler.join(10)
        self.assertFalse(self.coordinator.confirmer._confirm_handler.isAlive())

        self.reservation_processor.get_status()

        self.assertFalse( self.reservation_processor.is_expired() )

        self.assertRaises(
                coreExc.FailedToInteractError,
                self.reservation_processor.send_command,
                command
            )

        self.assertEquals( self.reservation_processor.get_status().status, Reservation.Reservation.POST_RESERVATION )

    def _fake_simple_lab_response(self):
        self.lab_mock.reserve_experiment(ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), "{}", mocker.ANY)
        self.mocker.result((SessionId.SessionId('my_lab_session_id'), 'ok', { 'address' : 'servexp:inst@mach' }))
        self.lab_mock.resolve_experiment_address('my_lab_session_id')
        self.mocker.result(CoordAddress("exp","inst","mach"))
        self.lab_mock.should_experiment_finish(SessionId.SessionId('my_lab_session_id'))
        self.mocker.result(0)
        self.mocker.replay()

    def _return_reserved(self):
        self.lab_mock.reserve_experiment(ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), "{}", mocker.ANY)
        self.mocker.result((SessionId.SessionId('my_lab_session_id'), 'ok', { 'address' : 'servexp:inst@mach' }))
        self.lab_mock.resolve_experiment_address('my_lab_session_id')
        self.mocker.result(CoordAddress("exp","inst","mach"))
        self.mocker.count(1,2)

class FakeDatabase(object):
    def __init__(self):
        self.experiments_allowed = [
                generate_experiment_allowed(
                        100,
                        'ud-dummy',
                        'Dummy experiments'
                    )
            ]
        self.groups = [ Group.Group("5A") ]
        self.experiments = [ generate_experiment('ud-dummy', 'Dummy experiments') ]
        self.experiment_uses = [ generate_experiment_use("student2", self.experiments[0]) ], 1
        self.users = [ User.User("admin1", "Admin Test User", "admin1@deusto.es", Role.Role("administrator")) ]
        self.roles = [ Role.Role("student"), Role.Role("instructor"), Role.Role("administrator") ]

    def is_access_forward(self, db_session_id):
        return True

    def store_experiment_usage(self, db_session_id, experiment_usage):
        pass

    def list_experiments(self, db_session_id, exp_name = None, cat_name = None):
        return self.experiments_allowed

    def get_user_by_name(self, db_session_id):
        return self.users[0]

class FakeLocator(object):
    def __init__(self, lab):
        self.lab = lab

    def __getitem__(self, coord_addr):
        if laboratory_coordaddr == coord_addr:
            return self.lab
        raise Exception("Server not found")

def generate_experiment(exp_name,exp_cat_name):
    cat = Category.ExperimentCategory(exp_cat_name)
    client = Experiment.ExperimentClient("client", {})
    exp = Experiment.Experiment( exp_name, cat, '01/01/2007', '31/12/2007', client)
    return exp

def generate_experiment_allowed(time_allowed, exp_name, exp_cat_name):
    exp = generate_experiment(exp_name, exp_cat_name)
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed, 5, True, '%s::user' % exp_name, 1, 'user')

def generate_experiment_use(user_login, exp):
    exp_use = ExperimentUse.ExperimentUse(
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow(),
        exp,
        User.User(
            user_login,
            "Jaime Irurzun",
            "jaime.irurzun@opendeusto.es",
            Role.Role("student")),
        "unknown")
    return exp_use

def suite():
    return unittest.makeSuite(ReservationProcessorTestCase)

if __name__ == '__main__':
    unittest.main()

