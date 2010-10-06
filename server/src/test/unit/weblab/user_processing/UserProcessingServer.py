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

import unittest
import datetime
import time

import mocker

from   test.util.ModuleDisposer import case_uses_module
import test.unit.configuration as configuration_module

import weblab.user_processing.UserProcessingServer    as UserProcessingServer
import weblab.user_processing.UserProcessor           as UserProcessor
import weblab.user_processing.Reservation             as Reservation
import weblab.user_processing.coordinator.Confirmer   as Confirmer
import weblab.user_processing.coordinator.Coordinator as Coordinator
import voodoo.configuration.ConfigurationManager      as ConfigurationManager
import weblab.database.DatabaseSession                as DatabaseSession
import weblab.data.ServerType                         as ServerType
import weblab.data.ClientAddress                      as ClientAddress

import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions

import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.dto.Category as Category
import weblab.data.dto.Experiment as Experiment
import weblab.data.dto.ExperimentAllowed as ExperimentAllowed

import voodoo.sessions.SessionId as SessionId
import voodoo.gen.coordinator.CoordAddress  as CoordAddress

laboratory_coordaddr = CoordAddress.CoordAddress.translate_address(
        "server:laboratoryserver@labmachine"
    )

class UserProcessingServerTestCase(unittest.TestCase):
    def setUp(self):
        self.coord_address = CoordAddress.CoordAddress.translate_address( "server0:instance0@machine0" )

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.cfg_manager._set_value(UserProcessingServer.COORDINATOR_LABORATORY_SERVERS,
                    [ 'server:laboratoryserver@labmachine;inst|ud-dummy|Dummy experiments' ] )

        self.mocker  = mocker.Mocker()
        self.lab_mock = self.mocker.mock()

        self.locator = FakeLocator(self.lab_mock)

        # Clean the database
        coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager)
        coordinator._clean()

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
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        experiments = self.ups.list_experiments(sess_id)
        self.assertEquals(7, len(experiments) )

        experiment_names = list(( experiment.experiment.name for experiment in experiments ))

        self.assertTrue( 'ud-dummy' in experiment_names )
        
        self.ups.logout(sess_id)


    def test_get_user_information(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        user = self.ups.get_user_information(sess_id)

        self.assertEquals("student2",user.login)
        self.assertEquals("Name of student 2",user.full_name)
        self.assertEquals("weblab@deusto.es",user.email)

        self.ups.logout(sess_id)


    def test_reserve_experiment(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        exp_id = ExperimentId.ExperimentId('this does not experiment','this neither')

        self.assertRaises(
            UserProcessingExceptions.UnknownExperimentIdException,
            self.ups.reserve_experiment,
            sess_id, exp_id, ClientAddress.ClientAddress("127.0.0.1")
        )

        exp_id = ExperimentId.ExperimentId('ud-dummy','Dummy experiments')
       
        lab_sess_id = SessionId.SessionId("lab_session_id")
        self.lab_mock.reserve_experiment(exp_id)
        self.mocker.result(lab_sess_id)
        self.mocker.count(0, 1)
        self.lab_mock.resolve_experiment_address(lab_sess_id)
        self.mocker.result(CoordAddress.CoordAddress.translate_address('foo:bar@machine'))
        self.mocker.count(0, 1)
        self.mocker.replay()

        reservation = self.ups.reserve_experiment(
            sess_id,
            exp_id,
            ClientAddress.ClientAddress("127.0.0.1")
        )

        self.assertTrue(
            isinstance(reservation,Reservation.Reservation)
        )

        self.ups.logout(sess_id)

    def test_reserve_experiment_raises_parsing_exception(self):
        self.cfg_manager._set_value(UserProcessingServer.COORDINATOR_LABORATORY_SERVERS,
                    [ 'this.doesnt.respect.the.regex' ] )

        # Clean the database
        coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager)
        coordinator._clean()

        # External server generation
        self.assertRaises(
                UserProcessingExceptions.CoordinationConfigurationParsingException,
                UserProcessingServer.UserProcessingServer,
                self.coord_address,
                self.locator,
                self.cfg_manager
            )

    def test_get_groups(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        groups = self.ups.get_groups(sess_id)
        self.assertEquals(1, len(groups) )

        groups_names = list(( group.name for group in groups ))

        self.assertTrue( '5A' in groups_names )
        
        self.ups.logout(sess_id)
    
    def test_get_roles(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        roles = self.ups.get_roles(sess_id)
        self.assertEquals(3, len(roles) )

        role_names = list( role.name for role in roles )

        self.assertTrue( 'student' in role_names )
        self.assertTrue( 'professor' in role_names )
        self.assertTrue( 'administrator' in role_names )
        
        self.ups.logout(sess_id)
        
    def test_get_users(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', 'student')
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        
        users = self.ups.get_users(sess_id)
        self.assertEquals(19, len(users) )
        
        users_names = list( user.login for user in users )
        
        self.assertTrue( 'student1' in users_names )
        
        self.ups.logout(sess_id)
        

    def test_get_experiments(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        experiments = self.ups.get_experiments(sess_id)
        self.assertEquals(11, len(experiments) )

        experiments_unique_names = list(( experiment.get_unique_name() for experiment in experiments ))

        self.assertTrue( 'ud-dummy@Dummy experiments' in experiments_unique_names )
        self.assertTrue( 'flashdummy@Dummy experiments' in experiments_unique_names )
        self.assertTrue( 'javadummy@Dummy experiments' in experiments_unique_names )
        self.assertTrue( 'ud-logic@PIC experiments' in experiments_unique_names )
        self.assertTrue( 'ud-pld@PLD experiments' in experiments_unique_names )
        self.assertTrue( 'ud-pld2@PLD experiments' in experiments_unique_names )
        self.assertTrue( 'ud-fpga@FPGA experiments' in experiments_unique_names )
        self.assertTrue( 'ud-gpib@GPIB experiments' in experiments_unique_names )
        self.assertTrue( 'ud-pic@PIC experiments' in experiments_unique_names )
        self.assertTrue( 'visirtest@Dummy experiments' in experiments_unique_names )
        self.assertTrue( 'vm@Dummy experiments' in experiments_unique_names)
        
        self.ups.logout(sess_id)

    def test_get_experiment_uses(self):
        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        from_date = datetime.datetime.utcnow()
        to_date = datetime.datetime.utcnow()
        group_id = 1
        experiment_id = 1
        
        self.ups._db_manager._gateway._insert_user_used_experiment("student2", "ud-fpga", "FPGA experiments", time.time(), "unknown", "fpga:process1@scabb", time.time())
        self.ups._db_manager._gateway._insert_ee_used_experiment("ee1", "ud-dummy", "Dummy experiments", time.time(), "unknown", "dummy:process1@plunder", time.time())
        
        experiment_uses = self.ups.get_experiment_uses(sess_id, from_date, to_date, group_id, experiment_id)
        self.assertEquals(2, len(experiment_uses) )

        experiment_names = list(( experiment_use.experiment.name for experiment_use in experiment_uses ))

        self.assertTrue( 'ud-fpga' in experiment_names )
        self.assertTrue( 'ud-dummy' in experiment_names )
        
        self.ups.logout(sess_id)


UserProcessingServerTestCase = case_uses_module(UserProcessingServer)(UserProcessingServerTestCase)
UserProcessingServerTestCase = case_uses_module(UserProcessor)(UserProcessingServerTestCase)
UserProcessingServerTestCase = case_uses_module(Confirmer)(UserProcessingServerTestCase)

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
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed)



def suite():
    return unittest.makeSuite(UserProcessingServerTestCase)

if __name__ == '__main__':
    unittest.main()

