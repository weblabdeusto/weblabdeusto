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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#

import unittest
import datetime

import mocker

import voodoo.gen.coordinator.CoordAddress as CoordAddress
from   test.util.module_disposer import case_uses_module

from weblab.core.server import WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER
import weblab.core.user_processor as UserProcessor
import weblab.core.coordinator.coordinator as Coordinator 
import weblab.core.coordinator.confirmer as Confirmer
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.coordinator.status as WebLabSchedulingStatus
from weblab.core.coordinator.config_parser import COORDINATOR_LABORATORY_SERVERS
import weblab.data.server_type as ServerType
import weblab.data.client_address as ClientAddress

import weblab.data.dto.users as Group
from weblab.data.experiments import ExperimentInstanceId
from weblab.data.experiments import ExperimentId
import weblab.data.dto.experiments as Category
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as ExperimentAllowed
import weblab.data.dto.experiments as ExperimentUse
import weblab.data.dto.users as User
import weblab.data.dto.users as Role

import weblab.db.session as DbSession

from weblab.core.coordinator.resource import Resource

import weblab.core.exc as coreExc

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

laboratory_coordaddr = CoordAddress.CoordAddress.translate_address(
        "server:laboratoryserver@labmachine"
    )

@case_uses_module(Confirmer)
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
        self.cfg_manager._set_value(COORDINATOR_LABORATORY_SERVERS, {
            'server:laboratoryserver@labmachine' : {
                'inst1|ud-dummy|Dummy experiments' : 'res_inst@res_type'
            }        
        })

        self.commands_store = TemporalInformationStore.CommandsTemporalInformationStore()

        self.coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager)
        self.coordinator._clean()
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), Resource("res_type", "res_inst"))

        self.processor = UserProcessor.UserProcessor(
                    self.locator,
                    {
                        'db_session_id' : DbSession.ValidDatabaseSessionId('my_db_session_id')
                    },
                    self.cfg_manager,
                    self.coordinator,
                    self.db,
                    self.commands_store
                )

    def tearDown(self):
        self.coordinator.stop()

    def test_reserve_unknown_experiment_name(self):
        self.assertRaises(
            coreExc.UnknownExperimentIdException,
            self.processor.reserve_experiment,
            ExperimentId('<invalid>', 'Dummy experiments'),
            "{}", "{}",
            ClientAddress.ClientAddress("127.0.0.1"),
            'uuid'
        )

    def test_reserve_unknown_experiment_category(self):
        self.assertRaises(
            coreExc.UnknownExperimentIdException,
            self.processor.reserve_experiment,
            ExperimentId('ud-dummy','<invalid>'),
            "{}", "{}",
            ClientAddress.ClientAddress("127.0.0.1"),
            'uuid'
        )

    def test_reserve_experiment_not_found(self):
        self.coordinator._clean()

        self.assertRaises(
            coreExc.NoAvailableExperimentFoundException,
            self.processor.reserve_experiment,
            ExperimentId('ud-dummy', 'Dummy experiments'),
            "{}", "{}",
            ClientAddress.ClientAddress("127.0.0.1"),
            'uuid'
        )

    def test_reserve_experiment_waiting_confirmation(self):
        self.coordinator.confirmer = FakeConfirmer()

        status = self.processor.reserve_experiment(
                    ExperimentId('ud-dummy', 'Dummy experiments'),
                    "{}", "{}",
                    ClientAddress.ClientAddress("127.0.0.1"), 'uuid'
                )

        self.assertTrue( isinstance( status, WebLabSchedulingStatus.WaitingConfirmationQueueStatus) )

    def test_reserve_experiment_repeated_uuid(self):
        self.coordinator.confirmer = FakeConfirmer()

        uuid = self.cfg_manager.get_value(WEBLAB_CORE_SERVER_UNIVERSAL_IDENTIFIER)

        status = self.processor.reserve_experiment(
                    ExperimentId('ud-dummy', 'Dummy experiments'),
                    "{}", '{ "%s" : [["%s","server x"]]}' % (UserProcessor.SERVER_UUIDS, uuid),
                    ClientAddress.ClientAddress("127.0.0.1"), uuid
                )

        self.assertTrue( 'replicated' )


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
        self.roles = [ Role.Role("student"), Role.Role("Professor"), Role.Role("Administrator") ]

    def is_access_forward(self, db_session_id):
        return True

    def store_experiment_usage(self, db_session_id, reservation_info, experiment_usage):
        pass

    def get_available_experiments(self, db_session_id):
        return self.experiments_allowed

    def retrieve_user_information(self, db_session_id):
        return self.users[0]

    def get_groups(self, db_session_id):
        return self.groups

    def get_roles(self, db_session_id):
        return self.roles

    def get_users(self, db_session_id):
        return self.users

    def get_experiments(self, db_session_id):
        return self.experiments

    def get_experiment_uses(self, db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
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
    return ExperimentAllowed.ExperimentAllowed(exp, time_allowed, 5, True)

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

