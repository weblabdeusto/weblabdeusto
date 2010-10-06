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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#

import unittest
import time
import datetime

import test.unit.configuration as configuration

import voodoo.configuration.ConfigurationManager as ConfigurationManager

import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.user_processing.database.DatabaseGateway as DatabaseGateway

import weblab.data.experiments.Usage as Usage
import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.Command as Command

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

class DatabaseMySQLGatewayTestCase(unittest.TestCase):

    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.gateway = DatabaseGateway.create_gateway(cfg_manager)
        self.gateway._delete_all_uses()
    
    def test_get_user_by_name(self):
        student = self.gateway.get_user_by_name('student2')

        self.assertEquals(student.login, 'student2')
        self.assertEquals(student.full_name, 'Name of student 2')
        self.assertRaises(
            DbExceptions.DbProvidedUserNotFoundException,
            self.gateway.get_user_by_name,
            'studentXX'
        )        

    def test_list_experiments(self):
        student1 = self.gateway.get_user_by_name('student1')
        student2 = self.gateway.get_user_by_name('student2')
        
        experiments = self.gateway.list_experiments(student1.login)
        self.assertEquals(len(experiments), 5)

        experiments = self.gateway.list_experiments(student2.login)
        self.assertEquals(len(experiments), 7)

        experiment_names = list( ( experiment.experiment.name for experiment in experiments ))

        self.assertTrue( 'ud-fpga' in experiment_names )
        self.assertTrue( 'ud-pld' in experiment_names )
        self.assertTrue( 'ud-gpib' in experiment_names )

    def test_store_experiment_usage(self):
        session = self.gateway.Session()
        student1 = self.gateway._get_user(session, 'student1')

        initial_usage = Usage.ExperimentUsage()
        initial_usage.start_date    = time.time()
        initial_usage.end_date      = time.time()
        initial_usage.from_ip       = "130.206.138.16"
        initial_usage.experiment_id = ExperimentId.ExperimentId("ud-dummy","Dummy experiments")
        initial_usage.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")

        file1 = Usage.FileSent(
                    'path/to/file1',
                    '{sha}12345',
                    time.time()
            )
        
        file2 = Usage.FileSent(
                    'path/to/file2',
                    '{sha}123456',
                    time.time(),
                    Command.Command('response'),
                    time.time(),
                    file_info = 'program'
            )

        command1 = Usage.CommandSent(
                    Command.Command("your command1"),
                    time.time()
            )
        
        command2 = Usage.CommandSent(
                    Command.Command("your command2"),
                    time.time(),
                    Command.Command("your response2"),
                    time.time()
            )

        initial_usage.append_command(command1)
        initial_usage.append_command(command2)
        initial_usage.append_file(file1)
        initial_usage.append_file(file2)
        
        self.gateway.store_experiment_usage(student1.login, initial_usage)

        usages = self.gateway.list_usages_per_user(student1.login)
        self.assertEquals(len(usages), 1)
        usage = usages[0]

        self.assertEquals( initial_usage.start_date, usage.start_date)
        if initial_usage.end_date is not None:
            self.assertEquals( initial_usage.end_date, usage.end_date)
        self.assertEquals( initial_usage.from_ip, usage.from_ip)
        self.assertEquals( initial_usage.experiment_id, usage.experiment_id)
        self.assertEquals( initial_usage.coord_address, usage.coord_address)

        full_usage = self.gateway.retrieve_usage(usage.experiment_use_id)

        self.assertEquals( initial_usage.start_date, full_usage.start_date)
        if initial_usage.end_date is not None:
            self.assertEquals( initial_usage.end_date, full_usage.end_date)
        self.assertEquals( initial_usage.from_ip, full_usage.from_ip)
        self.assertEquals( initial_usage.experiment_id, full_usage.experiment_id)
        self.assertEquals( initial_usage.coord_address, full_usage.coord_address)

        self.assertEquals( 2, len(full_usage.commands) )
        self.assertEquals( command1.command, full_usage.commands[0].command)
        self.assertEquals( command1.timestamp_before, full_usage.commands[0].timestamp_before)
        self.assertEquals( command1.response, full_usage.commands[0].response)
        if command1.timestamp_after is not None:
            self.assertEquals( command1.timestamp_after, full_usage.commands[0].timestamp_after)
        
        self.assertEquals( command2.command, full_usage.commands[1].command)
        self.assertEquals( command2.timestamp_before, full_usage.commands[1].timestamp_before)
        self.assertEquals( command2.response, full_usage.commands[1].response)
        if command2.timestamp_after is not None:
            self.assertEquals( command2.timestamp_after, full_usage.commands[1].timestamp_after)

        self.assertEquals( 2, len(full_usage.sent_files) )

        self.assertEquals( file1.file_sent, full_usage.sent_files[0].file_sent)
        self.assertEquals( file1.file_hash, full_usage.sent_files[0].file_hash)
        self.assertEquals( file1.file_info, full_usage.sent_files[0].file_info)
        self.assertEquals( file1.timestamp_before, full_usage.sent_files[0].timestamp_before)
        self.assertEquals( file1.response, full_usage.sent_files[0].response)
        if file1.timestamp_after is not None:
            self.assertEquals( file1.timestamp_after, full_usage.sent_files[0].timestamp_after)

        self.assertEquals( file2.file_sent, full_usage.sent_files[1].file_sent)
        self.assertEquals( file2.file_hash, full_usage.sent_files[1].file_hash)
        self.assertEquals( file2.file_info, full_usage.sent_files[1].file_info)
        self.assertEquals( file2.timestamp_before, full_usage.sent_files[1].timestamp_before)
        self.assertEquals( file2.response, full_usage.sent_files[1].response)
        if file2.timestamp_after is not None:
            self.assertEquals( file2.timestamp_after, full_usage.sent_files[1].timestamp_after)  
        
    def test_gather_permissions(self):
        session = self.gateway.Session()
        student2 = self.gateway._get_user(session, "student2")
        permissions = self.gateway._gather_permissions(session, student2, "experiment_allowed")
        
        # PLD (User Permissions)
        pld_permissions = [ perm for perm in permissions if perm.get_parameter("experiment_permanent_id").value == "ud-pld"]
        self.assertEquals(1, len(pld_permissions) )

        first_permission = pld_permissions[0]
        self.assertEquals(len(first_permission.parameters), 3)
        self.assertEquals(first_permission.get_parameter('experiment_permanent_id').value,'ud-pld')
        self.assertEquals(first_permission.get_parameter('experiment_category_id').value, 'PLD experiments')
        self.assertEquals(first_permission.get_parameter('time_allowed').value, '100')
        self.assertEquals(self.gateway._get_float_parameter_from_permission(session, first_permission, 'time_allowed'), 100.0)
        self.assertRaises(
                DbExceptions.InvalidPermissionParameterFormatException,
                self.gateway._get_float_parameter_from_permission,
                session,
                first_permission,
                'experiment_permanent_id'
            )
        self.assertEquals(first_permission.get_permission_type().name, 'experiment_allowed')

        # GPIB (User Permission)
        gpib_permissions = [ perm for perm in permissions if perm.get_parameter("experiment_permanent_id").value == "ud-gpib"]
        self.assertEquals(1, len(gpib_permissions) )

        second_permission = gpib_permissions[0]        
        self.assertEquals(len(second_permission.parameters), 3)
        self.assertEquals(second_permission.get_parameter('experiment_permanent_id').value, 'ud-gpib')
        self.assertEquals(second_permission.get_parameter('experiment_category_id').value, 'GPIB experiments')
        self.assertEquals(second_permission.get_parameter('time_allowed').value, '150')
        self.assertEquals(second_permission.get_permission_type().name, 'experiment_allowed')

        self.assertEquals(first_permission.get_permission_type(), second_permission.get_permission_type())        
        self.assertEquals(
                first_permission.get_parameter('experiment_permanent_id').permission_type_parameter,
                second_permission.get_parameter('experiment_permanent_id').permission_type_parameter,
            )
        
        self.assertEquals(second_permission.get_parameter('experiment_permanent_id').get_name(), 'experiment_permanent_id')
        self.assertEquals(second_permission.get_parameter('experiment_permanent_id').get_datatype(), 'string')

        # FPGA (Group Permissions)
        fpga_permissions = [ perm for perm in permissions if perm.get_parameter("experiment_permanent_id").value == "ud-fpga"]
        self.assertEquals(1, len(fpga_permissions) )

        fpga_permission = fpga_permissions[0]
        self.assertEquals(len(fpga_permission.parameters), 3)
        self.assertEquals(fpga_permission.get_parameter('experiment_permanent_id').value, 'ud-fpga')
        self.assertEquals(fpga_permission.get_parameter('experiment_category_id').value, 'FPGA experiments')
        self.assertEquals(fpga_permission.get_parameter('time_allowed').value, '30')
        self.assertEquals(fpga_permission.get_permission_type().name, 'experiment_allowed')
        self.assertEquals(fpga_permission.get_parameter('experiment_permanent_id').get_name(), 'experiment_permanent_id')
        self.assertEquals(fpga_permission.get_parameter('experiment_permanent_id').get_datatype(), 'string')   

    def test_get_groups(self):
        student1 = self.gateway.get_user_by_name('student1')
        student2 = self.gateway.get_user_by_name('student2')
        
        groups1 = self.gateway.get_groups(student1.login)
        self.assertEquals(len(groups1), 1)

        groups2 = self.gateway.get_groups(student2.login)
        self.assertEquals(len(groups2), 1)

        groups1_names = list( ( group.name for group in groups1 ))

        self.assertTrue( '5A' in groups1_names ) 
        
    def test_get_roles(self):
        roles = self.gateway.get_roles()
        
        self.assertEquals(len(roles), 3)
        
        user_roles = list ( role.name for role in roles )
        
        expected_roles = ('student', 'professor', 'administrator')
        
        for rn in expected_roles:
            self.assertTrue( rn in user_roles )
    
    def test_get_users(self):
        users = self.gateway.get_users()
        
        # Make sure that the number of users it returns matches the number of users
        # that we currently have in the test database.
        self.assertEquals(len(users), 19)
        
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
            

    def test_get_experiments(self):
        student2 = self.gateway.get_user_by_name('student2')
        
        experiments = self.gateway.get_experiments(student2.login)
        self.assertEquals(len(experiments), 11)

        experiments_names = list( ( experiment.name for experiment in experiments ))

        self.assertTrue( 'ud-dummy' in experiments_names )
        self.assertTrue( 'flashdummy' in experiments_names )
        self.assertTrue( 'javadummy' in experiments_names )
        self.assertTrue( 'ud-logic' in experiments_names )
        self.assertTrue( 'ud-pld' in experiments_names )
        self.assertTrue( 'ud-pld2' in experiments_names )
        self.assertTrue( 'ud-fpga' in experiments_names )
        self.assertTrue( 'ud-gpib' in experiments_names )
        self.assertTrue( 'ud-pic' in experiments_names )
        self.assertTrue( 'visirtest' in experiments_names )
        self.assertTrue( 'vm' in experiments_names )

    def test_get_experiment_uses(self):
        student2 = self.gateway.get_user_by_name('student2')
        from_date = datetime.datetime.utcnow()
        to_date = datetime.datetime.utcnow()
        group_id = 1
        experiment_id = 1
        
        self.gateway._insert_user_used_experiment("student2", "ud-fpga", "FPGA experiments", time.time(), "unknown", "fpga:process1@scabb", time.time())
        self.gateway._insert_ee_used_experiment("ee1", "ud-dummy", "Dummy experiments", time.time(), "unknown", "dummy:process1@plunder", time.time())
        
        experiment_uses = self.gateway.get_experiment_uses(student2.login, from_date, to_date, group_id, experiment_id)
        self.assertEquals(len(experiment_uses), 2)

        experiment_uses_names = list( ( experiment_use.experiment.name for experiment_use in experiment_uses ))

        self.assertTrue( 'ud-dummy' in experiment_uses_names )
        self.assertTrue( 'ud-fpga' in experiment_uses_names )

    def test_get_experiment_uses_with_null_params(self):
        student2 = self.gateway.get_user_by_name('student2')
        from_date = None
        to_date = None
        group_id = None
        experiment_id = None
        
        self.gateway._insert_user_used_experiment("student2", "ud-fpga", "FPGA experiments", time.time(), "unknown", "fpga:process1@scabb", time.time())
        self.gateway._insert_ee_used_experiment("ee1", "ud-dummy", "Dummy experiments", time.time(), "unknown", "dummy:process1@plunder", time.time())
        
        experiment_uses = self.gateway.get_experiment_uses(student2.login, from_date, to_date, group_id, experiment_id)
        self.assertEquals(len(experiment_uses), 2)

        experiment_uses_names = list( ( experiment_use.experiment.name for experiment_use in experiment_uses ))

        self.assertTrue( 'ud-dummy' in experiment_uses_names )
        self.assertTrue( 'ud-fpga' in experiment_uses_names )

        
def suite():
    return unittest.makeSuite(DatabaseMySQLGatewayTestCase)

if __name__ == '__main__':
    unittest.main()