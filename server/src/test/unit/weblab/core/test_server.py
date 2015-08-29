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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import os
import unittest
import time

import mocker

from   test.util.wlcontext import wlcontext
from   test.util.module_disposer import case_uses_module
import test.unit.configuration as configuration_module

import weblab.core.server    as UserProcessingServer
import weblab.core.server as core_api
import weblab.core.user_processor           as UserProcessor
import weblab.core.reservations             as Reservation
import weblab.core.coordinator.confirmer   as Confirmer
import voodoo.configuration      as ConfigurationManager
from weblab.data import ValidDatabaseSessionId
import weblab.data.server_type                         as ServerType
from weblab.core.coordinator.gateway import create as coordinator_create, SQLALCHEMY

import weblab.core.coordinator.config_parser as CoordinationConfigurationParser

import weblab.core.exc as coreExc

from weblab.data.command import Command
from weblab.data.experiments import ExperimentId, ExperimentUsage, CommandSent, FileSent, FinishedReservationResult

import weblab.data.dto.experiments as Category
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as ExperimentAllowed

import voodoo.sessions.session_id as SessionId
from voodoo.gen import CoordAddress

laboratory_coordaddr = CoordAddress.translate(
        "server:laboratoryserver@labmachine"
    )

@case_uses_module(UserProcessingServer)
@case_uses_module(Confirmer)
class UserProcessingServerTestCase(unittest.TestCase):
    """Note: We will test the underlying layers from this level to make the testing task less repetitive."""

    def setUp(self):
        self.coord_address = CoordAddress.translate( "server0:instance0@machine0" )

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS,
                    { 'server:laboratoryserver@labmachine' : { 'inst|ud-dummy|Dummy experiments' : 'dummy1@dummy boards' } } )
        self.cfg_manager._set_value("core_number", 0)

        self.mocker  = mocker.Mocker()
        self.lab_mock = self.mocker.mock()

        self.locator = FakeLocator(self.lab_mock)

        # Clean the database
        coordinator = coordinator_create(SQLALCHEMY, self.locator, self.cfg_manager)
        coordinator._clean()
        coordinator.stop()

        # External server generation
        self.ups = WrappedUPS(
                self.coord_address,
                self.locator,
                self.cfg_manager
            )

        self.ups._db_manager._delete_all_uses()

    def tearDown(self):
        self.ups.stop()

    #########
    # TESTS #
    #########

    def test_reserve_session(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

        session_manager = self.ups._session_manager

        sess = session_manager.get_session(sess_id)
        self.assertEquals(sess['db_session_id'].username, db_sess_id.username)
        with wlcontext(self.ups, session_id = sess_id):
            core_api.logout()

    def test_list_experiments(self):
        # student1
        db_sess_id1 = ValidDatabaseSessionId('student1', "student")
        sess_id1, _ = self.ups._reserve_session(db_sess_id1)

        with wlcontext(self.ups, session_id = sess_id1):
            experiments = core_api.list_experiments()

            self.assertLessEqual(5, len(experiments) )

            experiment_names = list(( experiment.experiment.name for experiment in experiments ))
            self.assertTrue( 'ud-dummy' in experiment_names )
            self.assertTrue( 'ud-logic' in experiment_names )
            self.assertTrue( 'ud-fpga' in experiment_names )
            self.assertTrue( 'flashdummy' in experiment_names )
            self.assertTrue( 'javadummy' in experiment_names )

            core_api.logout()

        # student2
        db_sess_id2 = ValidDatabaseSessionId('student2', "student")
        sess_id2, _ = self.ups._reserve_session(db_sess_id2)

        with wlcontext(self.ups, session_id = sess_id2):
            experiments = core_api.list_experiments()
            self.assertEquals(7, len(experiments) )

            experiment_names = list(( experiment.experiment.name for experiment in experiments ))
            self.assertTrue( 'ud-dummy' in experiment_names )
            self.assertTrue( 'ud-fpga' in experiment_names )
            self.assertTrue( 'ud-pld' in experiment_names )
            self.assertTrue( 'ud-gpib' in experiment_names )
            self.assertTrue( 'ud-logic' in experiment_names )
            self.assertTrue( 'javadummy' in experiment_names )
            self.assertTrue( 'flashdummy' in experiment_names )

            core_api.logout()

    def test_get_user_information(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

        with wlcontext(self.ups, session_id = sess_id):
            user = core_api.get_user_information()

            self.assertEquals("student2",user.login)
            self.assertEquals("Name of student 2",user.full_name)
            self.assertEquals("weblab@deusto.es",user.email)

            core_api.logout()

    def test_get_reservation_info(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)
        exp_id = ExperimentId('ud-dummy','Dummy experiments')
        lab_sess_id = SessionId.SessionId("lab_session_id")

        self.lab_mock.reserve_experiment(exp_id, "{}")
        self.mocker.result(lab_sess_id)
        self.mocker.count(0, 1)
        self.lab_mock.resolve_experiment_address(lab_sess_id)
        self.mocker.result(CoordAddress.translate('foo:bar@machine'))
        self.mocker.count(0, 1)
        self.mocker.replay()

        with wlcontext(self.ups, session_id = sess_id):
            reservation = core_api.reserve_experiment( exp_id, "{}", "{}")

        with wlcontext(self.ups, reservation_id = reservation.reservation_id):
            reservation_info = core_api.get_reservation_info()
            self.assertEquals('ud-dummy', reservation_info.exp_name)
            self.assertEquals('Dummy experiments', reservation_info.cat_name)

        with wlcontext(self.ups, session_id = sess_id):
            core_api.logout()

    def test_reserve_experiment(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

        exp_id = ExperimentId('this does not experiment','this neither')
        
        with wlcontext(self.ups, session_id = sess_id):
            self.assertRaises(
                coreExc.UnknownExperimentIdError,
                core_api.reserve_experiment, exp_id, "{}", "{}" )

            exp_id = ExperimentId('ud-dummy','Dummy experiments')

            lab_sess_id = SessionId.SessionId("lab_session_id")

            self.lab_mock.reserve_experiment(exp_id, "{}")
            self.mocker.result(lab_sess_id)
            self.mocker.count(0, 1)
            self.lab_mock.resolve_experiment_address(lab_sess_id)
            self.mocker.result(CoordAddress.translate('foo:bar@machine'))
            self.mocker.count(0, 1)
            self.mocker.replay()


            reservation = core_api.reserve_experiment(exp_id, "{}", "{}")

            self.assertTrue( isinstance(reservation,Reservation.Reservation))

            core_api.logout()

    def test_get_experiment_use_by_id_found(self):
        reservations, usages = self._store_two_reservations()

        db_sess_id = ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups._reserve_session(db_sess_id)
        with wlcontext(self.ups, session_id = sess_id):
            finished_result = core_api.get_experiment_use_by_id(reservations[0])

            self.assertTrue( finished_result.is_finished() )

            # reservation_id1 is for student1, so it returns a real object (with a real experiment_use_id)
            finished_result.experiment_use.experiment_use_id = None
            self.assertEquals(FinishedReservationResult(usages[0].load_files('.')), finished_result)


    def test_get_experiment_uses_by_id_found(self):
        reservations, usages = self._store_two_reservations()

        db_sess_id = ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups._reserve_session(db_sess_id)
        with wlcontext(self.ups, session_id = sess_id):
            experiment_results = core_api.get_experiment_uses_by_id(reservations)
            
            self.assertEquals(2, len(experiment_results))

            self.assertTrue( experiment_results[0].is_finished() )
            # reservation_id1 is for student1, so it returns a real object (with a real experiment_use_id)
            experiment_results[0].experiment_use.experiment_use_id = None
            self.assertEquals(FinishedReservationResult(usages[0].load_files('.')), experiment_results[0])

            # reservation_id2 is for student2, and the session is for student1, so it is forbidden
            self.assertTrue(experiment_results[1].is_forbidden())

    def test_get_experiment_uses_by_id_notfound(self):
        reservations, usages = self._store_two_reservations()

        reservation1 = self._reserve_experiment()
        reservation2 = self._reserve_experiment()

        db_sess_id = ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups._reserve_session(db_sess_id)
        with wlcontext(self.ups, session_id = sess_id):
            experiment_results = core_api.get_experiment_uses_by_id((reservations[0], reservation1, reservation2))

            self.assertEquals(3, len(experiment_results))

            # reservation_id1 is for student1, so it returns a real object (with a real experiment_use_id)
            self.assertTrue(experiment_results[0].is_finished())
            experiment_results[0].experiment_use.experiment_use_id = None
            self.assertEquals(FinishedReservationResult(usages[0].load_files('.')), experiment_results[0])

            # reservation_id2 is for student2, and the session is for student1, so it returns None
            self.assertTrue( experiment_results[1].is_alive() )
            self.assertTrue( experiment_results[2].is_alive() )

    def _reserve_experiment(self):
        db_sess_id = ValidDatabaseSessionId('student1', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)
        with wlcontext(self.ups, session_id = sess_id):
            exp_id = ExperimentId('ud-dummy','Dummy experiments')

            lab_sess_id = SessionId.SessionId("lab_session_id")
            self.lab_mock.reserve_experiment(exp_id, "{}")
            self.mocker.result(lab_sess_id)
            self.mocker.count(0, 1)
            self.lab_mock.resolve_experiment_address(lab_sess_id)
            self.mocker.result(CoordAddress.translate('foo:bar@machine'))
            self.mocker.count(0, 1)
            self.mocker.replay()

            reservation = core_api.reserve_experiment(exp_id, "{}", "{}")
            return reservation.reservation_id


    def _store_two_reservations(self):
        #
        # Two users: student2, that started before "any" but finished after "any", and "any" then. Both use
        # the same experiment.
        #
        db_gw = self.ups._db_manager
        session = db_gw.Session()
        try:
            student1 = db_gw._get_user(session, 'student1')
            student2 = db_gw._get_user(session, 'student2')
        finally:
            session.close()

        reservation_id1 = SessionId.SessionId(u'5')

        initial_usage1 = ExperimentUsage()
        initial_usage1.start_date    = time.time()
        initial_usage1.end_date      = time.time()
        initial_usage1.from_ip       = u"130.206.138.16"
        initial_usage1.experiment_id = ExperimentId(u"ud-dummy",u"Dummy experiments")
        initial_usage1.coord_address = CoordAddress(u"machine1",u"instance1",u"server1")
        initial_usage1.reservation_id = reservation_id1.id
        initial_usage1.request_info = { 'permission_scope' : 'user', 'permission_id' : student1.id }

        valid_file_path = os.path.relpath(os.sep.join(('test','__init__.py')))
        file1 = FileSent( valid_file_path, u'{sha}12345', time.time())

        file2 = FileSent( valid_file_path, u'{sha}123456',
                    time.time(), Command(u'response'),
                    time.time(), file_info = u'program')

        command1 = CommandSent( Command(u"your command1"), time.time())
        command2 = CommandSent( Command(u"your command2"), time.time(),
                    Command(u"your response2"), time.time())

        initial_usage1.append_command(command1)
        initial_usage1.append_command(command2)
        initial_usage1.append_file(file1)
        initial_usage1.append_file(file2)

        reservation_id2 = SessionId.SessionId(u'6')

        initial_usage2 = ExperimentUsage()
        initial_usage2.start_date    = time.time()
        initial_usage2.end_date      = time.time()
        initial_usage2.from_ip       = u"130.206.138.16"
        initial_usage2.experiment_id = ExperimentId(u"ud-dummy",u"Dummy experiments")
        initial_usage2.coord_address = CoordAddress(u"machine1",u"instance1",u"server1")
        initial_usage2.reservation_id = reservation_id2.id
        initial_usage2.request_info = { 'permission_scope' : 'user', 'permission_id' : student2.id }

        file1 = FileSent( valid_file_path, u'{sha}12345', time.time())

        file2 = FileSent( valid_file_path, u'{sha}123456',
                    time.time(), Command(u'response'),
                    time.time(), file_info = u'program')

        command1 = CommandSent( Command(u"your command1"), time.time())

        command2 = CommandSent( Command(u"your command2"), time.time(),
                    Command(u"your response2"), time.time())

        initial_usage2.append_command(command1)
        initial_usage2.append_command(command2)
        initial_usage2.append_file(file1)
        initial_usage2.append_file(file2)

        self.ups._db_manager.store_experiment_usage('student1', initial_usage1)

        self.ups._db_manager.store_experiment_usage('student2', initial_usage2)

        return (reservation_id1, reservation_id2), (initial_usage1, initial_usage2)


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

class FakeFacade(object):
    def __init__(self, *args, **kwargs):
        pass
    def start(self):
        pass
    def stop(self):
        pass

class WrappedUPS(UserProcessingServer.UserProcessingServer):
    FACADE_SERVER = FakeFacade

def generate_experiment(exp_name,exp_cat_name):
    cat = Category.ExperimentCategory(exp_cat_name)
    client = Experiment.ExperimentClient("client", {})
    exp = Experiment.Experiment( exp_name, cat, '01/01/2007', '31/12/2007', client )
    return exp

def generate_experiment_allowed(time_allowed, exp_name, exp_cat_name):
    exp = generate_experiment(exp_name, exp_cat_name)
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed, 5, True, '%s::user' % exp_name, 1, 'user')



def suite():
    return unittest.makeSuite(UserProcessingServerTestCase)

if __name__ == '__main__':
    unittest.main()

