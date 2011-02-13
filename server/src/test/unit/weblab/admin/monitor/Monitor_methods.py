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

import time

from   test.util.ModuleDisposer import case_uses_module
import test.unit.configuration as configuration_module

import weblab.admin.monitor.Monitor_methods           as methods
import voodoo.configuration.ConfigurationManager      as ConfigurationManager
import weblab.user_processing.UserProcessingServer    as UserProcessingServer
import weblab.user_processing.coordinator.Coordinator as Coordinator 
import weblab.user_processing.coordinator.Confirmer   as Confirmer
import weblab.exceptions.user_processing.UserProcessingExceptions as UPSExc

import weblab.database.DatabaseSession                as DatabaseSession

import weblab.data.dto.Category as Category
import weblab.data.dto.Experiment as Experiment
import weblab.data.dto.ExperimentAllowed as ExperimentAllowed
import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.data.ServerType                         as ServerType
import weblab.data.ClientAddress                      as ClientAddress
from weblab.data.dto.User import User
from weblab.data.dto.Role import Role
from weblab.user_processing.coordinator.Resource import Resource

import voodoo.gen.coordinator.CoordAddress  as CoordAddress

class ConfirmerMock(object):
    def __init__(self, *args, **kwargs):
        pass

    def enqueue_confirmation(self, lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data):
        pass

    def enqueue_free_experiment(self, lab_coordaddress, lab_session_id):
        pass

class MonitorMethodsTestCase(unittest.TestCase):
    def setUp(self):

        def _find_server(server_type, name):
            return self.ups

        self._find_server_backup = methods._find_server
        methods._find_server     = _find_server

        self.locator = FakeLocator()
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value("core_coordinator_laboratory_servers", {})

        # With this one we clean everything before creating the UPS
        self.coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager, ConfirmerClass = ConfirmerMock)
        self.coordinator._clean()

        self.coord_address = CoordAddress.CoordAddress.translate_address( "server0:instance0@machine0" )

        self.ups = UserProcessingServer.UserProcessingServer(
                self.coord_address,
                self.locator,
                self.cfg_manager
            )
        
        self.ups._coordinator = self.coordinator
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId.ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), Resource("res_type", "res_inst"))


    def tearDown(self):
        methods._find_server = self._find_server_backup
        self.ups.stop()

    def test_list_experiments(self):
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId.ExperimentInstanceId('inst','ud-dummy2','Dummy experiments'), Resource("res_type", "res_inst"))

        expected = "ud-dummy@Dummy experiments\n"
        expected +=  "ud-dummy2@Dummy experiments\n"

        result   = methods.list_experiments.call()
        self.assertEquals(expected, result)

    def test_get_experiment_status__zero(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        result   = methods.get_experiment_status.call(category, experiment)
        self.assertEquals({}, result)
        

    def test_get_experiment_status__one_reservation(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        status, reservation_id = self.coordinator.reserve_experiment(ExperimentId.ExperimentId(experiment, category), 30, 5, '{}')

        result   = methods.get_experiment_status.call(category, experiment)
        self.assertEquals({reservation_id : status}, result)

    def test_list_all_users(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        first_time = time.time()

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
      
        result = methods.list_all_users.call()
        self.assertEquals(1, len(result))
        session_id, user_info, latest = result[0]

        current_time = time.time() + 1

        self.assertTrue( first_time <= latest <= current_time )
        self.assertEquals( 'student2', user_info.login )

    def test_list_all_users_invalid_user(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        first_time = time.time()

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        sess_mgr = self.ups._session_manager
        sess_obj = sess_mgr.get_session(sess_id)
        sess_obj.pop('user_information')
      
        result = methods.list_all_users.call()
        self.assertEquals(1, len(result))
        session_id, user_info, latest = result[0]

        current_time = time.time() + 1

        self.assertTrue( first_time <= latest <= current_time )
        self.assertEquals( '<unknown>', user_info.login )


    def test_get_experiment_ups_session_ids(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        # 
        # It returns only the sessions_ids of the experiments
        # 
        result = methods.get_experiment_ups_session_ids.call(category, experiment)
        self.assertEquals( [], result ) 

        self.ups.reserve_experiment( sess_id, ExperimentId.ExperimentId( experiment, category ), "{}", ClientAddress.ClientAddress( "127.0.0.1" ))

        result = methods.get_experiment_ups_session_ids.call(category, experiment)
        self.assertEquals( 1, len(result) )
        session_id, login, reservation_id = result[0]
        self.assertEquals( sess_id.id, session_id ) 
        self.assertEquals( "student2", login ) 

    def test_get_ups_session_ids_from_username(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id1, _ = self.ups.do_reserve_session(db_sess_id)

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id2, _ = self.ups.do_reserve_session(db_sess_id)

        sessions = methods.get_ups_session_ids_from_username.call("student2")
        self.assertEquals(set([sess_id1, sess_id2]), set(sessions))

    def test_get_reservation_id_no_one_using_it(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id1, _ = self.ups.do_reserve_session(db_sess_id)

        reservation_id = methods.get_reservation_id.call(sess_id1.id)
        self.assertEquals(None, reservation_id)

    def test_get_reservation_id_one_user(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        self.ups.reserve_experiment(sess_id, ExperimentId.ExperimentId( experiment, category ), "{}", ClientAddress.ClientAddress( "127.0.0.1" ))

        reservation_id = methods.get_reservation_id.call(sess_id.id)
        self.assertNotEquals(None, reservation_id)

    def test_kickout_from_coordinator(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)
        self.ups.reserve_experiment(sess_id, ExperimentId.ExperimentId( experiment, category ), "{}", ClientAddress.ClientAddress( "127.0.0.1" ))

        status = self.ups.get_reservation_status(sess_id)
        self.assertNotEquals( None, status )

        reservation_id = methods.get_reservation_id.call(sess_id.id)
        methods.kickout_from_coordinator.call(reservation_id)

        status = self.ups.get_reservation_status(sess_id)
        self.assertEquals( None, status )

    def test_kickout_from_ups(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = DatabaseSession.ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups.do_reserve_session(db_sess_id)

        methods.kickout_from_ups.call(sess_id.id)

        self.assertRaises( UPSExc.SessionNotFoundException,
                self.ups.get_reservation_status, sess_id)

class FakeLocator(object):
    def __init__(self):
        self.db  = FakeDatabase()

    def get_server(self, server_type):
        if server_type == ServerType.Database:
            return self.db
        raise Exception("Server not found")

    def get_server_from_coordaddr(self, coord_addr, server_type):
        raise Exception("Server not found")

class FakeDatabase(object):
    def __init__(self):
        self.experiments = [
                generate_experiment_allowed( 100, 'ud-dummy', 'Dummy experiments' )
            ]

    def store_experiment_usage(self, db_session_id, experiment_usage):
        pass

    def get_available_experiments(self, db_session_id):
        return self.experiments

    def retrieve_user_information(self, db_session_id):
        return User("student2", "Name of student 2", "porduna@tecnologico.deusto.es", Role("student"))

def generate_experiment(exp_name,exp_cat_name):
    cat = Category.ExperimentCategory(exp_cat_name)
    exp = Experiment.Experiment( exp_name, cat, '01/01/2007', '31/12/2007' )
    return exp

def generate_experiment_allowed(time_allowed, exp_name, exp_cat_name):
    exp = generate_experiment(exp_name, exp_cat_name)
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed)

MonitorMethodsTestCase = case_uses_module(Confirmer)(MonitorMethodsTestCase)
MonitorMethodsTestCase = case_uses_module(UserProcessingServer)(MonitorMethodsTestCase)

def suite():
    return unittest.makeSuite(MonitorMethodsTestCase)

if __name__ == '__main__':
    unittest.main()

