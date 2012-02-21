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

import os
import unittest
import datetime
import time

import mocker

from   test.util.module_disposer import case_uses_module
import test.unit.configuration as configuration_module

import weblab.core.server    as UserProcessingServer
import weblab.core.user_processor           as UserProcessor
import weblab.core.reservations             as Reservation
import weblab.core.coordinator.confirmer   as Confirmer
import weblab.core.coordinator.coordinator as Coordinator
import voodoo.configuration      as ConfigurationManager
import weblab.db.session                as DatabaseSession
import weblab.data.server_type                         as ServerType
import weblab.data.client_address                      as ClientAddress

import weblab.core.coordinator.config_parser as CoordinationConfigurationParser

import weblab.core.exc as coreExc

from weblab.data.command import Command
from weblab.data.experiments import ExperimentId, ExperimentUsage, CommandSent, FileSent, FinishedReservationResult

import weblab.data.dto.experiments as Category
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as ExperimentAllowed

import voodoo.sessions.session_id as SessionId
import voodoo.gen.coordinator.CoordAddress  as CoordAddress

laboratory_coordaddr = CoordAddress.CoordAddress.translate_address(
        "server:laboratoryserver@labmachine"
    )

@case_uses_module(UserProcessingServer)
@case_uses_module(UserProcessor)
@case_uses_module(Confirmer)
class UserProcessingServerTestCase(unittest.TestCase):
    """Note: We will test the underlying layers from this level to make the testing task less repetitive."""

    def setUp(self):
        self.coord_address = CoordAddress.CoordAddress.translate_address( "server0:instance0@machine0" )

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.cfg_manager._set_value(CoordinationConfigurationParser.COORDINATOR_LABORATORY_SERVERS,
                    { 'server:laboratoryserver@labmachine' : { 'inst|ud-dummy|Dummy experiments' : 'dummy1@dummy boards' } } )

        self.mocker  = mocker.Mocker()
        self.lab_mock = self.mocker.mock()

        self.locator = FakeLocator(self.lab_mock)

        # Clean the database
        coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager)
        coordinator._clean()
        coordinator.stop()

        # External server generation
        self.ups = WrappedUPS(
                self.coord_address,
                self.locator,
                self.cfg_manager
            )

        self.ups._db_manager._gateway._delete_all_uses()

    def tearDown(self):
        self.ups.stop()

    #########
    # TESTS #
    #########

    def test_reserve_session(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        session_manager = self.ups._session_manager

        sess = session_manager.get_session(sess_id)
        self.assertEquals(sess['db_session_id'].username, db_sess_id.username)
        self.ups.logout(sess_id)

    def test_list_experiments(self):
        # student1
        db_sess_id1 = DatabaseSession.ValidDatabaseSessionId('student1', "student")
        sess_id1, _ = self.ups.do_reserve_session(db_sess_id1)

        experiments = self.ups.list_experiments(sess_id1)
        self.assertEquals(5, len(experiments) )

        experiment_names = list(( experiment.experiment.name for experiment in experiments ))
        self.assertTrue( 'ud-dummy' in experiment_names )
        self.assertTrue( 'ud-logic' in experiment_names )
        self.assertTrue( 'ud-fpga' in experiment_names )
        self.assertTrue( 'flashdummy' in experiment_names )
        self.assertTrue( 'javadummy' in experiment_names )

        self.ups.logout(sess_id1)

        # student2
        db_sess_id2 = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id2, _ = self.ups.do_reserve_session(db_sess_id2)

        experiments = self.ups.list_experiments(sess_id2)
        self.assertEquals(7, len(experiments) )

        experiment_names = list(( experiment.experiment.name for experiment in experiments ))
        self.assertTrue( 'ud-dummy' in experiment_names )
        self.assertTrue( 'ud-fpga' in experiment_names )
        self.assertTrue( 'ud-pld' in experiment_names )
        self.assertTrue( 'ud-gpib' in experiment_names )
        self.assertTrue( 'ud-logic' in experiment_names )
        self.assertTrue( 'javadummy' in experiment_names )
        self.assertTrue( 'flashdummy' in experiment_names )

        self.ups.logout(sess_id2)

    def test_get_user_information(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        user = self.ups.get_user_information(sess_id)

        self.assertEquals("student2",user.login)
        self.assertEquals("Name of student 2",user.full_name)
        self.assertEquals("weblab@deusto.es",user.email)

        self.ups.logout(sess_id)

    def test_get_reservation_info(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        exp_id = ExperimentId('ud-dummy','Dummy experiments')

        lab_sess_id = SessionId.SessionId("lab_session_id")
        self.lab_mock.reserve_experiment(exp_id, "{}")
        self.mocker.result(lab_sess_id)
        self.mocker.count(0, 1)
        self.lab_mock.resolve_experiment_address(lab_sess_id)
        self.mocker.result(CoordAddress.CoordAddress.translate_address('foo:bar@machine'))
        self.mocker.count(0, 1)
        self.mocker.replay()

        reservation = self.ups.reserve_experiment(
            sess_id, exp_id, "{}", "{}",
            ClientAddress.ClientAddress("127.0.0.1")
        )

        reservation_info = self.ups.get_reservation_info(reservation.reservation_id)
        self.assertEquals('ud-dummy', reservation_info.exp_name)
        self.assertEquals('Dummy experiments', reservation_info.cat_name)

        self.ups.logout(sess_id)

    def test_reserve_experiment(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        exp_id = ExperimentId('this does not experiment','this neither')

        self.assertRaises(
            coreExc.UnknownExperimentIdError,
            self.ups.reserve_experiment,
            sess_id, exp_id, "{}", "{}", ClientAddress.ClientAddress("127.0.0.1")
        )

        exp_id = ExperimentId('ud-dummy','Dummy experiments')

        lab_sess_id = SessionId.SessionId("lab_session_id")
        self.lab_mock.reserve_experiment(exp_id, "{}")
        self.mocker.result(lab_sess_id)
        self.mocker.count(0, 1)
        self.lab_mock.resolve_experiment_address(lab_sess_id)
        self.mocker.result(CoordAddress.CoordAddress.translate_address('foo:bar@machine'))
        self.mocker.count(0, 1)
        self.mocker.replay()

        reservation = self.ups.reserve_experiment(
            sess_id, exp_id, "{}", "{}",
            ClientAddress.ClientAddress("127.0.0.1")
        )

        self.assertTrue( isinstance(reservation,Reservation.Reservation))

        self.ups.logout(sess_id)

    def _test_get_groups_with_permission(self, parent_id):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        groups = self.ups.get_groups(sess_id, parent_id)
        self.ups.logout(sess_id)

        return groups

    def test_get_groups_all(self):
        groups = self._test_get_groups_with_permission(parent_id=None)

        self.assertEquals(3, len(groups) )

        self.assertEquals('Course 2008/09', groups[0].name)
        self.assertEquals(2, len(groups[0].children) )
        self.assertEquals('Mechatronics', groups[0].children[0].name)
        self.assertEquals(0, len(groups[0].children[0].children) )
        self.assertEquals('Telecomunications', groups[0].children[1].name)
        self.assertEquals(0, len(groups[0].children[1].children) )

        self.assertEquals('Course 2009/10', groups[1].name)
        self.assertEquals(0, len(groups[1].children) )

    def test_get_groups_from_parent(self):
        all_groups = self._test_get_groups_with_permission(parent_id=None)
        self.assertEquals('Course 2008/09', all_groups[0].name)
        groups = self._test_get_groups_with_permission(parent_id=all_groups[0].id)

        self.assertEquals(2, len(groups) )

        self.assertEquals('Mechatronics', groups[0].name)
        self.assertEquals(0, len(groups[0].children) )

        self.assertEquals('Telecomunications', groups[1].name)
        self.assertEquals(0, len(groups[1].children) )

    def test_get_groups_without_permission(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        groups = self.ups.get_groups(sess_id, parent_id=None)
        self.ups.logout(sess_id)

        self.assertEquals(0, len(groups) )

    def test_get_experiments(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        experiments = self.ups.get_experiments(sess_id)
        self.ups.logout(sess_id)

        self.assertTrue( len(experiments) > 14 )
        unique_names = [ exp.get_unique_name() for exp in experiments ]
        self.assertTrue('flashdummy@Dummy experiments' in unique_names)
        self.assertTrue('javadummy@Dummy experiments'  in unique_names)
        self.assertTrue('ud-dummy@Dummy experiments'   in unique_names)
        self.assertTrue('visirtest@Dummy experiments'  in unique_names)
        self.assertTrue('vm@Dummy experiments'         in unique_names)
        self.assertTrue('ud-fpga@FPGA experiments'     in unique_names)
        self.assertTrue('ud-gpib@GPIB experiments'     in unique_names)
        self.assertTrue('ud-logic@PIC experiments'     in unique_names)
        self.assertTrue('ud-pic@PIC experiments'       in unique_names)
        self.assertTrue('ud-pld@PLD experiments'       in unique_names)
        self.assertTrue('ud-pld2@PLD experiments'      in unique_names)

    def test_get_experiments_without_permission(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        experiments = self.ups.get_experiments(sess_id)
        self.ups.logout(sess_id)

        self.assertEquals(0, len(experiments) )

    def test_get_experiment_use_by_id_found(self):
        reservations, usages = self._store_two_reservations()

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        finished_result = self.ups.get_experiment_use_by_id(sess_id, reservations[0])

        self.assertTrue( finished_result.is_finished() )

        # reservation_id1 is for student1, so it returns a real object (with a real experiment_use_id)
        finished_result.experiment_use.experiment_use_id = None
        self.assertEquals(FinishedReservationResult(usages[0].load_files('.')), finished_result)


    def test_get_experiment_uses_by_id_found(self):
        reservations, usages = self._store_two_reservations()

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        experiment_results = self.ups.get_experiment_uses_by_id(sess_id, reservations)
        
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

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        experiment_results = self.ups.get_experiment_uses_by_id(sess_id, (reservations[0], reservation1, reservation2))

        self.assertEquals(3, len(experiment_results))

        # reservation_id1 is for student1, so it returns a real object (with a real experiment_use_id)
        self.assertTrue(experiment_results[0].is_finished())
        experiment_results[0].experiment_use.experiment_use_id = None
        self.assertEquals(FinishedReservationResult(usages[0].load_files('.')), experiment_results[0])

        # reservation_id2 is for student2, and the session is for student1, so it returns None
        self.assertTrue( experiment_results[1].is_alive() )
        self.assertTrue( experiment_results[2].is_alive() )

    def _reserve_experiment(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        exp_id = ExperimentId('ud-dummy','Dummy experiments')

        lab_sess_id = SessionId.SessionId("lab_session_id")
        self.lab_mock.reserve_experiment(exp_id, "{}")
        self.mocker.result(lab_sess_id)
        self.mocker.count(0, 1)
        self.lab_mock.resolve_experiment_address(lab_sess_id)
        self.mocker.result(CoordAddress.CoordAddress.translate_address('foo:bar@machine'))
        self.mocker.count(0, 1)
        self.mocker.replay()

        reservation = self.ups.reserve_experiment(
            sess_id, exp_id, "{}", "{}",
            ClientAddress.ClientAddress("127.0.0.1"))
        return reservation.reservation_id


    def _store_two_reservations(self):
        #
        # Two users: student2, that started before "any" but finished after "any", and "any" then. Both use
        # the same experiment.
        #
        reservation_id1 = SessionId.SessionId(u'5')

        initial_usage1 = ExperimentUsage()
        initial_usage1.start_date    = time.time()
        initial_usage1.end_date      = time.time()
        initial_usage1.from_ip       = u"130.206.138.16"
        initial_usage1.experiment_id = ExperimentId(u"ud-dummy",u"Dummy experiments")
        initial_usage1.coord_address = CoordAddress.CoordAddress(u"machine1",u"instance1",u"server1") #.translate_address("server1:instance1@machine1")
        initial_usage1.reservation_id = reservation_id1.id

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
        initial_usage2.coord_address = CoordAddress.CoordAddress(u"machine1",u"instance1",u"server1") #.translate_address("server1:instance1@machine1")
        initial_usage2.reservation_id = reservation_id2.id

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

        self.ups._db_manager._gateway.store_experiment_usage('student1', initial_usage1)

        self.ups._db_manager._gateway.store_experiment_usage('student2', initial_usage2)

        return (reservation_id1, reservation_id2), (initial_usage1, initial_usage2)


    def _test_get_experiment_uses(self, from_date, to_date, group_id, use_experiment_id, start_row, end_row, sort_by):
        #
        # Two users: student2, that started before "any" but finished after "any", and "any" then. Both use
        # the same experiment.
        #
        experiment_id = self.ups._db_manager._gateway._insert_user_used_experiment("student2", "ud-fpga", "FPGA experiments", time.time() - 3600, "192.168.1.1", "fpga:process1@scabb", '5', time.time() - 1000)
        self.ups._db_manager._gateway._insert_user_used_experiment("any", "ud-fpga", "FPGA experiments", time.time() - 1800, "127.0.0.1", "fpga:process1@scabb", '6', time.time() - 1700)
        if not use_experiment_id:
            experiment_id = None
        elif use_experiment_id == 'other':
            experiment_id += 2

        #
        # student4 uses a different experiment, after both student2 and any
        #
        self.ups._db_manager._gateway._insert_user_used_experiment("student4", "ud-dummy", "Dummy experiments", time.time() - 60, "unknown", "fpga:process1@scabb", '7', time.time() - 60)

        self.ups._db_manager._gateway._insert_ee_used_experiment("ee1", "ud-dummy", "Dummy experiments", time.time() - 60, "unknown", "dummy:process1@plunder", '8', time.time() - 60)
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        experiment_uses, experiment_uses_number = self.ups.get_experiment_uses(sess_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)
        self.ups.logout(sess_id)

        return experiment_uses, experiment_uses_number

    def test_get_experiment_uses_without_filtering(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('start_date',))

        self.assertEquals(2, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )
        self.assertEquals('student2',  experiment_uses[0].agent.login)
        self.assertEquals('any',  experiment_uses[1].agent.login)

    def test_get_experiment_uses_filtering_future_start_date(self):
        future_time = datetime.datetime(3000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(future_time, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('start_date',))

        self.assertEquals(0, len(experiment_uses) )
        self.assertEquals(0, experiment_uses_number )

    def test_get_experiment_uses_filtering_past_start_date(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, long_time_ago, None, use_experiment_id, 0, 50, ('start_date',))

        self.assertEquals(0, len(experiment_uses) )
        self.assertEquals(0, experiment_uses_number )

    def test_get_experiment_uses_filtering_group_with_single_user(self):
        groups = self._test_get_groups_with_permission(None)
        mechatronics_class = groups[0].children[0]

        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        # Group mechatronics has only student4
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), mechatronics_class.id, use_experiment_id, 0, 50, ('start_date',))

        self.assertEquals(1, len(experiment_uses) )
        self.assertEquals(1, experiment_uses_number )

        self.assertEquals('student4',  experiment_uses[0].agent.login)

    def test_get_experiment_uses_filtering_group_with_single_user_parent_group(self):
        groups = self._test_get_groups_with_permission(None)
        parent_group = groups[0]

        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        # Group mechatronics has only student2 and student4
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), parent_group.id, use_experiment_id, 0, 50, ('start_date',))

        self.assertEquals(2, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )

        self.assertTrue(set(('student2','student4')), set([experiment_use.agent.login for experiment_use in experiment_uses]))

    def test_get_experiment_uses_filtering_empty_experiment_id(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = 'other'
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('start_date',))

        self.assertEquals(0, len(experiment_uses) )
        self.assertEquals(0, experiment_uses_number )

    def test_get_experiment_uses_filtering_starting_by_higher_than_count(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 50, 100, ('start_date',))

        self.assertEquals(0, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )

    def test_get_experiment_uses_filtering_starting_by_lower_than_zero(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 0, ('start_date',))

        self.assertEquals(0, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )

    def test_get_experiment_uses_filtering_sorting_by_end_date(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('end_date',))

        self.assertEquals(2, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )
        self.assertEquals('any',       experiment_uses[0].agent.login)
        self.assertEquals('student2',  experiment_uses[1].agent.login)

    def test_get_experiment_uses_filtering_sorting_by_end_date_desc(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('-end_date',))

        self.assertEquals(2, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )
        self.assertEquals('student2',  experiment_uses[0].agent.login)
        self.assertEquals('any',       experiment_uses[1].agent.login)


    def test_get_experiment_uses_filtering_sorting_by_origin(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('origin',))

        self.assertEquals(2, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )
        self.assertEquals('127.0.0.1',  experiment_uses[0].origin)
        self.assertEquals('192.168.1.1',  experiment_uses[1].origin)

    def test_get_experiment_uses_filtering_sorting_by_origin_desc(self):
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = True
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('-origin',))

        self.assertEquals(2, len(experiment_uses) )
        self.assertEquals(2, experiment_uses_number )
        self.assertEquals('192.168.1.1',  experiment_uses[0].origin)
        self.assertEquals('127.0.0.1',  experiment_uses[1].origin)


    def test_get_experiment_uses_filtering_sorting_by_experiment_name(self):
        # Experiment_name is not a field of DbUserUsedExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('experiment_name',))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        # ud-*d*ummy comes before ud-*f*pga
        self.assertEquals('ud-dummy',  experiment_uses[0].experiment.name)
        self.assertEquals('ud-fpga',   experiment_uses[1].experiment.name)
        self.assertEquals('ud-fpga',   experiment_uses[2].experiment.name)

    def test_get_experiment_uses_filtering_sorting_by_experiment_name_desc(self):
        # Experiment_name is not a field of DbUserUsedExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('-experiment_name',))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        # ud-*d*ummy comes before ud-*f*pga
        self.assertEquals('ud-fpga',   experiment_uses[0].experiment.name)
        self.assertEquals('ud-fpga',   experiment_uses[1].experiment.name)
        self.assertEquals('ud-dummy',  experiment_uses[2].experiment.name)

    def test_get_experiment_uses_filtering_sorting_by_experiment_category(self):
        # Experiment_name is not a field of DbUserUsedExperiment, neither in DbExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('experiment_category',))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        # *D*ummy experiments comes before *F*PGA experiments
        self.assertEquals('Dummy experiments', experiment_uses[0].experiment.category.name)
        self.assertEquals('FPGA experiments',  experiment_uses[1].experiment.category.name)
        self.assertEquals('FPGA experiments',  experiment_uses[2].experiment.category.name)

    def test_get_experiment_uses_filtering_sorting_by_experiment_category_desc(self):
        # Experiment_name is not a field of DbUserUsedExperiment, neither in DbExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('-experiment_category',))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        # *D*ummy experiments comes before *F*PGA experiments
        self.assertEquals('FPGA experiments',  experiment_uses[0].experiment.category.name)
        self.assertEquals('FPGA experiments',  experiment_uses[1].experiment.category.name)
        self.assertEquals('Dummy experiments', experiment_uses[2].experiment.category.name)

    def test_get_experiment_uses_filtering_sorting_by_agent_name(self):
        # agent_name is not a field of DbUserUsedExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('agent_name',))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        self.assertEquals('any',       experiment_uses[0].agent.login)
        self.assertEquals('student2',  experiment_uses[1].agent.login)
        self.assertEquals('student4',  experiment_uses[2].agent.login)

    def test_get_experiment_uses_filtering_sorting_by_agent_name_desc(self):
        # agent_name is not a field of DbUserUsedExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('-agent_name',))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        self.assertEquals('student4',  experiment_uses[0].agent.login)
        self.assertEquals('student2',  experiment_uses[1].agent.login)
        self.assertEquals('any',       experiment_uses[2].agent.login)


    def test_get_experiment_uses_filtering_sorting_by_experiment_name_and_then_agent_name(self):
        # agent_name is not a field of DbUserUsedExperiment
        long_time_ago = datetime.datetime(2000, 1, 1)
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(long_time_ago, datetime.datetime.utcnow(), None, use_experiment_id, 0, 50, ('experiment_name','agent_login'))

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        # ud-dummy goes first, then "any" (both "any" and "student2" use the same experiment)
        self.assertEquals('student4',  experiment_uses[0].agent.login)
        self.assertEquals('any',       experiment_uses[1].agent.login)
        self.assertEquals('student2',  experiment_uses[2].agent.login)

    def test_get_experiment_uses_with_null_params(self):
        use_experiment_id = False
        experiment_uses, experiment_uses_number = self._test_get_experiment_uses(None, None, None, use_experiment_id, None, None, None)

        self.assertEquals(3, len(experiment_uses) )
        self.assertEquals(3, experiment_uses_number )
        self.assertEquals('ud-fpga',   experiment_uses[0].experiment.name)
        self.assertEquals('ud-fpga',   experiment_uses[1].experiment.name)
        self.assertEquals('ud-dummy',  experiment_uses[2].experiment.name)

    def test_get_experiment_uses_without_permission(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        result = self.ups.get_experiment_uses(sess_id)
        self.ups.logout(sess_id)

        self.assertEquals(0, len(result) )

    def test_get_roles(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        roles = self.ups.get_roles(sess_id)
        self.ups.logout(sess_id)

        self.assertEquals(3, len(roles) )
        role_names = list( role.name for role in roles )
        self.assertTrue( 'student' in role_names )
        self.assertTrue( 'professor' in role_names )
        self.assertTrue( 'administrator' in role_names )

    def test_get_roles_without_permission(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        roles = self.ups.get_roles(sess_id)
        self.ups.logout(sess_id)

        self.assertEquals(0, len(roles) )

    def test_get_users(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', 'student')

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        users = self.ups.get_users(sess_id)
        self.ups.logout(sess_id)

        # Make sure that the number of users it returns matches the number of users
        # that we currently have in the test database.
        self.assertEquals(len(users), 27)

        user_logins = list( ( user.login for user in users ) )

        # Make sure every single user login we currently have is present
        for i in range(1,9):
            self.assertTrue( "student%d" % i in user_logins )
        for i in range(1, 4):
            self.assertTrue( "admin%d" % i in user_logins )
            self.assertTrue( "prof%d" % i in user_logins )
            self.assertTrue( "studentLDAP%d" % i in user_logins )
        self.assertTrue("any" in user_logins)
        self.assertTrue("studentLDAPwithoutUserAuth" in user_logins)

        # Check mails
        user_mails = list( user.email for user in users )
        user_mails_set = set(user_mails)
        self.assertEquals(len(user_mails_set), 1)
        self.assertTrue( "weblab@deusto.es" in user_mails_set )
        # Check a few login / full name pairs
        user_logins_names = list( (user.login, user.full_name) for user in users )
        for i in range(1, 9):
            self.assertTrue( ("student%d" % i, "Name of student %d" % i) in user_logins_names )
        for i in range(1, 3):
            self.assertTrue( ("admin%d" % i, "Name of administrator %d" % i) in user_logins_names )

    def test_get_users_without_permission(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        users = self.ups.get_users(sess_id)
        self.ups.logout(sess_id)

        self.assertEquals(0, len(users) )

    def test_get_user_permissions(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student1', "student")

        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        permissions = self.ups.get_user_permissions(sess_id)
        self.ups.logout(sess_id)

        self.assertEquals(7, len(permissions))

        self.assertEquals('experiment_allowed', permissions[0].name)
        self.assertEquals(3, len(permissions[0].parameters))

        # We only check the first permission's parameters, all of them would be death...
        self.assertEquals('experiment_permanent_id', permissions[0].parameters[0].name)
        self.assertEquals('string',                  permissions[0].parameters[0].datatype)
        self.assertEquals('ud-fpga',                 permissions[0].parameters[0].value)

        self.assertEquals('experiment_category_id',  permissions[0].parameters[1].name)
        self.assertEquals('string',                  permissions[0].parameters[1].datatype)
        self.assertEquals('FPGA experiments',        permissions[0].parameters[1].value)

        self.assertEquals('time_allowed',            permissions[0].parameters[2].name)
        self.assertEquals('float',                   permissions[0].parameters[2].datatype)
        self.assertEquals('300',                     permissions[0].parameters[2].value)

        self.assertEquals('experiment_allowed', permissions[1].name)
        self.assertEquals(3, len(permissions[1].parameters))

        self.assertEquals('experiment_allowed', permissions[2].name)
        self.assertEquals(3, len(permissions[2].parameters))

        self.assertEquals('experiment_allowed', permissions[3].name)
        self.assertEquals(3, len(permissions[3].parameters))

        self.assertEquals('experiment_allowed', permissions[4].name)
        self.assertEquals(3, len(permissions[4].parameters))

        self.assertEquals('experiment_allowed', permissions[5].name)
        self.assertEquals(3, len(permissions[5].parameters))

        self.assertEquals('admin_panel_access', permissions[6].name)
        self.assertEquals(1, len(permissions[6].parameters))

        # Ok, the last one too... it's short!
        self.assertEquals('full_privileges', permissions[6].parameters[0].name)
        self.assertEquals('bool',            permissions[6].parameters[0].datatype)
        self.assertEquals('1',               permissions[6].parameters[0].value)


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
    exp = Experiment.Experiment( exp_name, cat, '01/01/2007', '31/12/2007' )
    return exp

def generate_experiment_allowed(time_allowed, exp_name, exp_cat_name):
    exp = generate_experiment(exp_name, exp_cat_name)
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed, 5, True)



def suite():
    return unittest.makeSuite(UserProcessingServerTestCase)

if __name__ == '__main__':
    unittest.main()

