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
from __future__ import print_function, unicode_literals

import unittest

import time

from   test.util.wlcontext import wlcontext
from   test.util.module_disposer import case_uses_module
import test.unit.configuration as configuration_module

import weblab.admin.monitor.monitor_methods           as methods
import voodoo.configuration      as ConfigurationManager
import weblab.core.server    as UserProcessingServer
import weblab.core.server    as core_api
import weblab.core.coordinator.confirmer   as Confirmer
import weblab.core.exc as core_exc
from weblab.core.coordinator.config_parser import COORDINATOR_LABORATORY_SERVERS
from weblab.core.coordinator.gateway import create as coordinator_create, SQLALCHEMY

from weblab.data import ValidDatabaseSessionId

import weblab.data.dto.experiments as Category
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as ExperimentAllowed
from weblab.data.experiments import ExperimentId
from weblab.data.experiments import ExperimentInstanceId
import weblab.data.server_type                         as ServerType
from weblab.data.dto.users import User
from weblab.data.dto.users import Role
from weblab.core.coordinator.resource import Resource

from voodoo.gen import CoordAddress

class ConfirmerMock(object):
    def __init__(self, *args, **kwargs):
        pass

    def enqueue_confirmation(self, lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data, resource_type_name):
        pass

    def enqueue_free_experiment(self, lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id):
        pass

@case_uses_module(Confirmer)
@case_uses_module(UserProcessingServer)
class MonitorMethodsTestCase(unittest.TestCase):
    def setUp(self):

        self.maxDiff = 2000

        def _find_server(server_type, name):
            return self.ups

        self._find_server_backup = methods._find_server
        methods._find_server     = _find_server

        self.locator = FakeLocator()
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value(COORDINATOR_LABORATORY_SERVERS, {
            'server:laboratoryserver@labmachine' : {
                'inst|ud-dummy|Dummy experiments' : 'res_inst@res_type'
            }
        })

        # With this one we clean everything before creating the UPS
        self.coordinator = coordinator_create(SQLALCHEMY, self.locator, self.cfg_manager, ConfirmerClass = ConfirmerMock)
        self.coordinator._clean()

        self.coord_address = CoordAddress.translate( "server0:instance0@machine0" )

        self.ups = UserProcessingServer.UserProcessingServer(
                self.coord_address,
                self.locator,
                self.cfg_manager
            )

        self.ups._coordinator.stop()
        self.ups._coordinator = self.coordinator
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), Resource("res_type", "res_inst"))


    def tearDown(self):
        methods._find_server = self._find_server_backup
        self.ups.stop()

    def test_list_experiments(self):
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId('inst','ud-dummy2','Dummy experiments'), Resource("res_type", "res_inst"))

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

        status, reservation_id = self.coordinator.reserve_experiment(ExperimentId(experiment, category), 30, 5, True, '{}', {}, {})

        result   = methods.get_experiment_status.call(category, experiment)
        self.assertEquals({reservation_id : status}, result)

    def test_list_all_users(self):
        first_time = time.time()

        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

        result = methods.list_all_users.call()
        self.assertEquals(1, len(result))
        session_id, user_info, latest = result[0]

        current_time = time.time() + 1

        self.assertTrue( first_time <= latest <= current_time )
        self.assertEquals( 'student2', user_info.login )

    def test_list_all_users_invalid_user(self):
        first_time = time.time()

        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

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

        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

        #
        # It returns only the sessions_ids of the experiments
        #
        result = methods.get_experiment_ups_session_ids.call(category, experiment)
        self.assertEquals( [], result )
        
        with wlcontext(self.ups, session_id = sess_id):
            status = core_api.reserve_experiment(ExperimentId( experiment, category ), "{}", "{}")

        result = methods.get_experiment_ups_session_ids.call(category, experiment)
        self.assertEquals( 1, len(result) )
        session_id, login, reservation_id = result[0]
        self.assertEquals( status.reservation_id.id.split(';')[0], session_id )
        self.assertEquals( "student2", login )

    def test_get_ups_session_ids_from_username(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id1, _ = self.ups._reserve_session(db_sess_id)

        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id2, _ = self.ups._reserve_session(db_sess_id)

        sessions = methods.get_ups_session_ids_from_username.call("student2")
        self.assertEquals(set([sess_id1, sess_id2]), set(sessions))

    def test_get_reservation_id_no_one_using_it(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id1, _ = self.ups._reserve_session(db_sess_id)

        reservation_id = methods.get_reservation_id.call(sess_id1.id)
        self.assertEquals(None, reservation_id)

    def test_get_reservation_id_one_user(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)
        with wlcontext(self.ups, session_id = sess_id):
            core_api.reserve_experiment(ExperimentId( experiment, category ), "{}", "{}")

        reservation_id = methods.get_reservation_id.call(sess_id.id)
        self.assertNotEquals(None, reservation_id)

    def test_kickout_from_coordinator(self):
        category   = "Dummy experiments"
        experiment = "ud-dummy"

        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)
        with wlcontext(self.ups, session_id = sess_id):
            status = core_api.reserve_experiment(ExperimentId( experiment, category ), "{}", "{}")

            reservation_session_id = status.reservation_id
            
            with wlcontext(self.ups, reservation_id = reservation_session_id, session_id = sess_id):
                status = core_api.get_reservation_status()
                self.assertNotEquals( None, status )

                reservation_id = methods.get_reservation_id.call(sess_id.id)
                methods.kickout_from_coordinator.call(reservation_id)

                self.assertRaises( core_exc.NoCurrentReservationError, core_api.get_reservation_status)

    def test_kickout_from_ups(self):
        db_sess_id = ValidDatabaseSessionId('student2', "student")
        sess_id, _ = self.ups._reserve_session(db_sess_id)

        methods.kickout_from_ups.call(sess_id.id)
        with wlcontext(self.ups, session_id = sess_id):
            self.assertRaises( core_exc.SessionNotFoundError, core_api.get_reservation_status)

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
    client = Experiment.ExperimentClient('myclient', {})
    exp = Experiment.Experiment( exp_name, cat, '01/01/2007', '31/12/2007', client )
    return exp

def generate_experiment_allowed(time_allowed, exp_name, exp_cat_name):
    exp = generate_experiment(exp_name, exp_cat_name)
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed, 5, True, 'permission::user', 1, 'user')

def suite():
    return unittest.makeSuite(MonitorMethodsTestCase)

if __name__ == '__main__':
    unittest.main()

