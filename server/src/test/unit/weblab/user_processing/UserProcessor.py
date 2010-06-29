#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import unittest
import time
import datetime

import mocker

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.sessions.SessionId as SessionId
from   test.util.ModuleDisposer import case_uses_module

import weblab.user_processing.UserProcessor as UserProcessor
import weblab.user_processing.Reservation as Reservation
import weblab.user_processing.coordinator.Coordinator as Coordinator 
import weblab.user_processing.coordinator.Confirmer as Confirmer
import weblab.data.ServerType as ServerType
import weblab.data.ClientAddress as ClientAddress

import weblab.data.Command as Command
import weblab.data.dto.Group as Group
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.dto.Category as Category
import weblab.data.dto.Experiment as Experiment
import weblab.data.dto.ExperimentAllowed as ExperimentAllowed
import weblab.data.dto.ExperimentUse as ExperimentUse
import weblab.data.dto.User as User
import weblab.data.dto.Role as Role

import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions
import weblab.exceptions.laboratory.LaboratoryExceptions as LaboratoryExceptions

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

laboratory_coordaddr = CoordAddress.CoordAddress.translate_address(
        "server:laboratoryserver@labmachine"
    )

class UserProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.mocker  = mocker.Mocker()
        self.lab_mock = self.mocker.mock()

        self.locator = FakeLocator(
                lab = self.lab_mock
            )
        self.db      = FakeDatabase()

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager)
        self.coordinator._clean()
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId.ExperimentInstanceId('inst','ud-dummy','Dummy experiments'))

        self.processor = UserProcessor.UserProcessor(
                    self.locator,
                    {
                        'db_session_id' : 'my_db_session_id'
                    },
                    self.cfg_manager,
                    self.coordinator,
                    self.db
                )

    def test_reserve_unknown_experiment_name(self):
        self.assertRaises(
            UserProcessingExceptions.UnknownExperimentIdException,
            self.processor.reserve_experiment,
            ExperimentId.ExperimentId('<invalid>', 'Dummy experiments'),
            ClientAddress.ClientAddress("127.0.0.1")
        )

    def test_reserve_unknown_experiment_category(self):
        self.assertRaises(
            UserProcessingExceptions.UnknownExperimentIdException,
            self.processor.reserve_experiment,
            ExperimentId.ExperimentId('ud-dummy','<invalid>'),
            ClientAddress.ClientAddress("127.0.0.1")
        )

    def test_reserve_experiment_not_found(self):
        self.coordinator._clean()

        self.assertRaises(
            UserProcessingExceptions.NoAvailableExperimentFoundException,
            self.processor.reserve_experiment,
            ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
            ClientAddress.ClientAddress("127.0.0.1")
        )

    def test_reserve_experiment_waiting_confirmation(self):
        self.coordinator.confirmer = FakeConfirmer()

        reservation = self.processor.reserve_experiment(
                    ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                    ClientAddress.ClientAddress("127.0.0.1")
                )

        self.assertTrue( isinstance( reservation, Reservation.WaitingConfirmationReservation) )

    def test_is_polling(self):
        self.assertFalse( self.processor.is_polling() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        self.assertTrue( self.processor.is_polling() )

        self.processor.finished_experiment()

        self.assertFalse( self.processor.is_polling() )

    def test_is_expired_didnt_expire(self):
        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        self.assertFalse( self.processor.is_expired() )

        self.processor.finished_experiment()

        self.assertTrue( self.processor.is_expired() )
    
    def test_is_expired_expired_without_expiration_time_set(self):
        time_mock = self.mocker.mock()
        time_mock.time()

        poll_time = self.cfg_manager.get_value(UserProcessor.EXPERIMENT_POLL_TIME)
        added = poll_time + 5

        self.mocker.result(time.time() + added)
        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        self.processor.time_module = time_mock

        self.assertTrue( self.processor.is_expired() )

    def test_is_expired_expired_due_to_expiration_time(self):
        self._return_reserved()

        poll_time = self.cfg_manager.get_value(UserProcessor.EXPERIMENT_POLL_TIME)
        added = poll_time - 5 # for example
        self.db.experiments_allowed[0].time_allowed = poll_time - 10
        self.assertTrue( added > 0 )

        time_mock = self.mocker.mock()
        time_mock.time()
        self.mocker.result(time.time() + added)

        self.mocker.replay()

        # 
        # Not polling, so yes, expired
        self.assertTrue( self.processor.is_expired() )

        #
        # Reserve the experiment
        reservation_status = self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
   
        self.coordinator.confirmer._confirm_handler.join()

        reservation_status = self.processor.get_reservation_status()

        self.assertTrue( isinstance(reservation_status, Reservation.ConfirmedReservation) )

        self.processor.time_module = time_mock

        self.assertTrue( self.processor.is_expired() )

    def test_finished_experiment_ok(self):
        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()
        self.processor.finished_experiment()

    def test_finished_experiment_coordinator_error(self):
        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        # Force the coordinator to fail when invoking finish_reservation
        self.coordinator.finish_reservation = lambda *args: 10 / 0

        self.assertRaises(
                UserProcessingExceptions.FailedToFreeReservationException,
                self.processor.finished_experiment
            )

    def test_send_file_ok(self):
        file_content = "SAMPLE CONTENT"
        lab_response  = "LAB RESPONSE"
        file_info    = 'program'
        self._return_reserved()

        self.lab_mock.send_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.result(lab_response)

        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )

        self.coordinator.confirmer._confirm_handler.join()
        reservation_status = self.processor.get_reservation_status()

        self.assertFalse( self.processor.is_expired() )

        response = self.processor.send_file(file_content, file_info)

        self.assertEquals(lab_response, response)

        self.assertFalse( self.processor.is_expired() )

        self.processor.finished_experiment()

        self.assertTrue( self.processor.is_expired() )

    def test_send_file_session_not_found_in_lab(self):
        self._return_reserved()

        file_content = "SAMPLE CONTENT"
        lab_response  = "LAB RESPONSE"
        file_info    = "program"
        self.lab_mock.send_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.throw( 
                LaboratoryExceptions.SessionNotFoundInLaboratoryServerException("problem@laboratory") 
            )
        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        reservation_status = self.processor.get_reservation_status()

        self.assertFalse( self.processor.is_expired() )

        self.assertRaises(
                UserProcessingExceptions.NoCurrentReservationException,
                self.processor.send_file,
                file_content,
                file_info
            )

        self.assertTrue( self.processor.is_expired() )

    def test_send_file_failed_to_send(self):
        self._return_reserved()

        file_content = "SAMPLE CONTENT"
        lab_response  = "LAB RESPONSE"
        file_info    = "program"
        self.lab_mock.send_file(SessionId.SessionId('my_lab_session_id'), file_content, file_info)
        self.mocker.throw( 
                LaboratoryExceptions.FailedToSendFileException("problem@laboratory") 
            )
        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        reservation_status = self.processor.get_reservation_status()

        self.assertFalse( self.processor.is_expired() )

        self.assertRaises(
                UserProcessingExceptions.FailedToSendFileException,
                self.processor.send_file,
                file_content,
                file_info
            )

        self.assertTrue( self.processor.is_expired() )

    def test_send_command_ok(self):
        self._return_reserved()

        command = Command.Command("Your command")
        lab_response  = "LAB RESPONSE"
        self.lab_mock.send_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.result(lab_response)

        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        reservation_status = self.processor.get_reservation_status()

        self.assertFalse( self.processor.is_expired() )

        response = self.processor.send_command(command)

        self.assertEquals(lab_response, response)

        self.assertFalse( self.processor.is_expired() )

        self.processor.finished_experiment()

        self.assertTrue( self.processor.is_expired() )

    def test_send_command_session_not_found_in_lab(self):
        self._return_reserved()

        command = Command.Command("Your command")
        lab_response  = "LAB RESPONSE"
        self.lab_mock.send_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.throw( 
                LaboratoryExceptions.SessionNotFoundInLaboratoryServerException("problem@laboratory") 
            )
        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        reservation_status = self.processor.get_reservation_status()

        self.assertFalse( self.processor.is_expired() )

        self.assertRaises(
                UserProcessingExceptions.NoCurrentReservationException,
                self.processor.send_command,
                command
            )

        self.assertTrue( self.processor.is_expired() )

    def test_send_command_failed_to_send(self):
        self._return_reserved()

        command = Command.Command("Your command")
        lab_response  = "LAB RESPONSE"
        self.lab_mock.send_command(SessionId.SessionId('my_lab_session_id'), command)
        self.mocker.throw( 
                LaboratoryExceptions.FailedToSendCommandException("problem@laboratory") 
            )
        self.mocker.replay()

        self.assertTrue( self.processor.is_expired() )

        self.processor.reserve_experiment(
                ExperimentId.ExperimentId('ud-dummy', 'Dummy experiments'),
                ClientAddress.ClientAddress("127.0.0.1")
            )
        self.coordinator.confirmer._confirm_handler.join()

        reservation_status = self.processor.get_reservation_status()

        self.assertFalse( self.processor.is_expired() )

        self.assertRaises(
                UserProcessingExceptions.FailedToSendCommandException,
                self.processor.send_command,
                command
            )

        self.assertTrue( self.processor.is_expired() )


    def _return_reserved(self):
        self.lab_mock.reserve_experiment(ExperimentInstanceId.ExperimentInstanceId('inst','ud-dummy','Dummy experiments'))
        self.mocker.result(SessionId.SessionId('my_lab_session_id'))
        self.lab_mock.resolve_experiment_address('my_lab_session_id')
        self.mocker.result(CoordAddress.CoordAddress("exp","inst","mach"))
        self.mocker.count(1,2)

UserProcessorTestCase = case_uses_module(Confirmer)(UserProcessorTestCase)

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
        self.experiment_uses = [ generate_experiment_use("student2", self.experiments[0]) ]
        self.users = [ User.User("admin1", "Admin Test User", "admin1@deusto.es", Role.Role("administrator")) ]

    def store_experiment_usage(self, db_session_id, experiment_usage):
        pass

    def get_available_experiments(self, db_session_id):
        return self.experiments_allowed

    def retrieve_user_information(self, db_session_id):
        pass

    def get_groups(self, db_session_id):
        return self.groups
    
    def get_users(self, db_session_id):
        return self.users

    # TODO: remove second return?
    def get_experiments(self, db_session_id):
        return self.experiments
        return self.groups

    def get_experiment_uses(self, db_session_id, from_date, to_date, group_id, experiment_id):
        return self.experiment_uses

class FakeLocator(object):
    def __init__(self, lab):
        self.lab = lab

    def get_server(self, server_type):
        if server_type == ServerType.Laboratory:
            return self.lab
        raise Exception("Server not found")

    def get_server_from_coordaddr(self, coord_addr, server_type):
        if server_type == ServerType.Laboratory and laboratory_coordaddr == coord_addr:
            return self.lab
        raise Exception("Server not found")

class FakeConfirmer(object):
    def enqueue_confirmation(self, *args):
        pass
    def enqueue_free_experiment(self, *args):
        pass

def generate_experiment(exp_name,exp_cat_name):
    cat = Category.ExperimentCategory(exp_cat_name)
    exp = Experiment.Experiment(
        exp_name,
        cat,
        '01/01/2007',
        '31/12/2007'
    )
    return exp

def generate_experiment_allowed(time_allowed, exp_name, exp_cat_name):
    exp = generate_experiment(exp_name, exp_cat_name)
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed)

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
    return unittest.makeSuite(UserProcessorTestCase)

if __name__ == '__main__':
    unittest.main()

