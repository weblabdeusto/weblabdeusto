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
import datetime

import mocker

from voodoo.gen import CoordAddress
from   test.util.module_disposer import case_uses_module

import weblab.configuration_doc as configuration_doc

import weblab.core.user_processor as UserProcessor
import weblab.core.coordinator.confirmer as Confirmer
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.coordinator.status as WebLabSchedulingStatus
from weblab.core.coordinator.config_parser import COORDINATOR_LABORATORY_SERVERS
import weblab.data.server_type as ServerType
from weblab.core.coordinator.gateway import create as coordinator_create, SQLALCHEMY

import weblab.data.dto.users as Group
from weblab.data.experiments import ExperimentInstanceId
from weblab.data.experiments import ExperimentId
import weblab.data.dto.experiments as Category
import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as ExperimentAllowed
import weblab.data.dto.experiments as ExperimentUse
import weblab.data.dto.users as User
import weblab.data.dto.users as Role
from weblab.data import ValidDatabaseSessionId

from weblab.core.coordinator.resource import Resource

import weblab.core.exc as coreExc

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

laboratory_coordaddr = CoordAddress.translate(
        "server:laboratoryserver@labmachine"
    )

@case_uses_module(Confirmer)
class UserProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.mocker  = mocker.Mocker()
        self.lab_mock = self.mocker.mock()

        self.locator = FakeLocator( lab = self.lab_mock )
        self.db      = FakeDatabase()

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value(COORDINATOR_LABORATORY_SERVERS, {
            'server:laboratoryserver@labmachine' : {
                'inst1|ud-dummy|Dummy experiments' : 'res_inst@res_type'
            }
        })

        self.commands_store = TemporalInformationStore.CommandsTemporalInformationStore()

        self.coordinator = coordinator_create(SQLALCHEMY, self.locator, self.cfg_manager, ConfirmerClass = FakeConfirmer)
        self.coordinator._clean()
        self.coordinator.add_experiment_instance_id("server:laboratoryserver@labmachine", ExperimentInstanceId('inst','ud-dummy','Dummy experiments'), Resource("res_type", "res_inst"))

        self.processor = UserProcessor.UserProcessor(
                    self.locator,
                    {
                        'db_session_id' : ValidDatabaseSessionId('my_db_session_id')
                    },
                    self.cfg_manager, self.coordinator, self.db, self.commands_store
                )

    def tearDown(self):
        self.coordinator.stop()

    def test_reserve_unknown_experiment_name(self):
        self.assertRaises(
            coreExc.UnknownExperimentIdError,
            self.processor.reserve_experiment,
            ExperimentId('<invalid>', 'Dummy experiments'),
            "{}", "{}", "127.0.0.1", 'uuid'
        )

    def test_reserve_unknown_experiment_category(self):
        self.assertRaises(
            coreExc.UnknownExperimentIdError,
            self.processor.reserve_experiment,
            ExperimentId('ud-dummy','<invalid>'),
            "{}", "{}", "127.0.0.1", 'uuid'
        )

    def test_reserve_experiment_not_found(self):
        self.coordinator._clean()

        self.assertRaises(
            coreExc.NoAvailableExperimentFoundError,
            self.processor.reserve_experiment,
            ExperimentId('ud-dummy', 'Dummy experiments'),
            "{}", "{}", "127.0.0.1", 'uuid'
        )

    def test_reserve_experiment_waiting_confirmation(self):
        status = self.processor.reserve_experiment(
                    ExperimentId('ud-dummy', 'Dummy experiments'),
                    "{}", "{}", "127.0.0.1", 'uuid')
        self.assertTrue( isinstance( status, WebLabSchedulingStatus.WaitingConfirmationQueueStatus) )

    def test_reserve_experiment_repeated_uuid(self):
        uuid = self.cfg_manager.get_doc_value(configuration_doc.CORE_UNIVERSAL_IDENTIFIER)

        status = self.processor.reserve_experiment(
                    ExperimentId('ud-dummy', 'Dummy experiments'),
                    "{}", '{ "%s" : [["%s","server x"]]}' % (UserProcessor.SERVER_UUIDS, uuid),
                    "127.0.0.1", uuid)
        self.assertEquals( 'replicated', status )


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
        return [ exp for exp in self.experiments_allowed if exp.experiment.name == exp_name and exp.experiment.category.name == cat_name ]

    def get_user_by_name(self, db_session_id):
        return self.users[0]

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
    def __init__(self, *args):
        pass
    def enqueue_confirmation(self, *args):
        pass
    def enqueue_free_experiment(self, *args):
        pass

def generate_experiment(exp_name,exp_cat_name):
    cat = Category.ExperimentCategory(exp_cat_name)
    client = Experiment.ExperimentClient("client", {})
    exp = Experiment.Experiment(
        exp_name,
        cat,
        '01/01/2007',
        '31/12/2007',
        client
    )
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
    return unittest.makeSuite(UserProcessorTestCase)

if __name__ == '__main__':
    unittest.main()

