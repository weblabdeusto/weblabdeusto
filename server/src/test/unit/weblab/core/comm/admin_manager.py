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

import test.unit.configuration as configuration
import voodoo.configuration as ConfigurationManager

import weblab.core.comm.admin_manager as AdminFacadeManager
import weblab.comm.codes as RFCodes
import weblab.comm.manager as RFM
import weblab.core.comm.codes as UserProcessingRFCodes

import weblab.data.dto.experiments as Experiment
import weblab.data.dto.experiments as Category
import weblab.data.dto.users as Group

from weblab.data.dto.users import User
from weblab.data.dto.users import Role
from weblab.data.dto.experiments import ExperimentUse

import weblab.core.exc as coreExc
import weblab.exc as WebLabExceptions
import voodoo.gen.exceptions.exceptions as VoodooExceptions

class MockUPS(object):

    def __init__(self):
        super(MockUPS, self).__init__()
        self.arguments     = {}
        self.return_values = {}
        self.exceptions    = {}

    def get_roles(self, session_id):
        self.arguments['get_roles'] = (session_id, )
        if self.exceptions.has_key('get_roles'):
            raise self.exceptions['get_roles']
        return self.return_values['get_roles']

    def get_groups(self, session_id, parent_id):
        self.arguments['get_groups'] = (session_id, parent_id, )
        if self.exceptions.has_key('get_groups'):
            raise self.exceptions['get_groups']
        return self.return_values['get_groups']

    def get_users(self, session_id):
        self.arguments['get_users'] = (session_id, )
        if self.exceptions.has_key('get_users'):
            raise self.exceptions['get_users']
        return self.return_values['get_users']

    def get_experiments(self, session_id):
        self.arguments['get_experiments'] = (session_id, )
        if self.exceptions.has_key('get_experiments'):
            raise self.exceptions['get_experiments']
        return self.return_values['get_experiments']

    def get_experiment_uses(self, session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
        self.arguments['get_experiment_uses'] = (session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)
        if self.exceptions.has_key('get_experiment_uses'):
            raise self.exceptions['get_experiment_uses']
        return self.return_values['get_experiment_uses']


class AdminFacadeManagerJSONTestCase(unittest.TestCase):

    def setUp(self):

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration)

        self.mock_ups = MockUPS()

        server_admin_mail = self.cfg_manager.get_value(RFM.SERVER_ADMIN_EMAIL, RFM.DEFAULT_SERVER_ADMIN_EMAIL)
        self.weblab_general_error_message = RFM.UNEXPECTED_ERROR_MESSAGE_TEMPLATE % server_admin_mail 

        self.rfm = AdminFacadeManager.AdminRemoteFacadeManagerJSON(
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

    def test_return_get_groups(self):
        expected_sess_id = {'id' : 'whatever'}
        groups = self._generate_groups()

        self.mock_ups.return_values['get_groups'] = groups

        self.assertEquals(
                groups,
                self.rfm.get_groups(expected_sess_id)
            )

        self.assertEquals(
                expected_sess_id['id'],
                self.mock_ups.arguments['get_groups'][0].id
            )

    def test_return_get_users(self):
        expected_sess_id = {'id' : "whatever"}
        users = self._generate_users()

        self.mock_ups.return_values['get_users'] = users

        self.assertEquals(
                users,
                self.rfm.get_users(expected_sess_id)
            )

        self.assertEquals(
                expected_sess_id['id'],
                self.mock_ups.arguments['get_users'][0].id
            )


    def test_return_get_roles(self):
        expected_sess_id = {'id' : "whatever"}
        roles = self._generate_roles()

        self.mock_ups.return_values['get_roles'] = roles

        self.assertEquals(
                roles,
                self.rfm.get_roles(expected_sess_id)
            )

        self.assertEquals(
                expected_sess_id['id'],
                self.mock_ups.arguments['get_roles'][0].id
            )


    def test_return_get_experiments(self):
        expected_sess_id = {'id' : "whatever"}
        experiments = self._generate_experiments()

        self.mock_ups.return_values['get_experiments'] = experiments

        self.assertEquals(
                experiments,
                self.rfm.get_experiments(expected_sess_id)
            )

        self.assertEquals(
                expected_sess_id['id'],
                self.mock_ups.arguments['get_experiments'][0].id
            )

    def test_return_get_experiment_uses(self):
        expected_sess_id = {'id' : "whatever"}
        experiment_uses = _generate_experiment_uses()

        self.mock_ups.return_values['get_experiment_uses'] = experiment_uses

        self.assertEquals(
                experiment_uses,
                self.rfm.get_experiment_uses(expected_sess_id, None, None, None, None, None, None, None)
            )

        self.assertEquals(
                expected_sess_id['id'],
                self.mock_ups.arguments['get_experiment_uses'][0].id
            )

    def _generate_real_mock_raising(self, method, exception, message):
        self.mock_ups.exceptions[method] = exception(message)


    def _test_exception(self, method, args, exc_to_raise, exc_message, expected_code, expected_exc_message):
        self._generate_real_mock_raising(method, exc_to_raise, exc_message )
        getattr(self.rfm, method)(*args)
        self.fail('exception expected')

    def _test_general_exceptions(self, method, *args):
        MESSAGE = "The exception message"

        # Production mode: A general error message is received
        self.cfg_manager._set_value(RFM.DEBUG_MODE, False)

        self._test_exception(method, args,  
                        coreExc.WebLabCoreException, MESSAGE, 
                        'JSON:' + UserProcessingRFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,  
                        WebLabExceptions.WebLabException, MESSAGE, 
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,  
                        VoodooExceptions.GeneratorException, MESSAGE, 
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

        self._test_exception(method, args,  
                        Exception, MESSAGE, 
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)            

        # Debug mode: The error message is received
        self.cfg_manager._set_value(RFM.DEBUG_MODE, True)

        self._test_exception(method, args,  
                        coreExc.WebLabCoreException, MESSAGE, 
                        'JSON:' + UserProcessingRFCodes.UPS_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,  
                        WebLabExceptions.WebLabException, MESSAGE, 
                        'JSON:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, MESSAGE)

        self._test_exception(method, args,  
                        VoodooExceptions.GeneratorException, MESSAGE, 
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


def suite():
    test_cases = ( unittest.makeSuite(AdminFacadeManagerJSONTestCase), )

    return unittest.TestSuite(test_cases)

if __name__ == '__main__':
    unittest.main()

