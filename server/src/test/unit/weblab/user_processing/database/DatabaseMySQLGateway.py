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

import test.unit.configuration as configuration

import voodoo.configuration.ConfigurationManager as ConfigurationManager
import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.data.experiments.Usage as Usage
import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.data.Command as Command

import weblab.user_processing.database.DatabaseGateway as DatabaseGateway
import weblab.user_processing.database.DatabaseMySQLGateway as DatabaseMySQLGateway
import weblab.database.DatabaseAccountManager as DAM

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

from weblab.database.DatabaseConstants import STUDENT, PROFESSOR, ADMINISTRATOR, EXTERNAL_ENTITY
from weblab.database.DatabaseConstants import READ, WRITE, NAME

class DatabaseMySQLGatewayTestCase(unittest.TestCase):
    def setUp(self):
        student_read_user  = DAM.DatabaseUserInformation( 'wl_student_read', 'wl_student_read_password')
        student_write_user = DAM.DatabaseUserInformation( 'wl_student_write', 'wl_student_write_password')
        self.student_credentials = { NAME  : STUDENT, READ  : student_read_user, WRITE : student_write_user }

        professor_read_user  = DAM.DatabaseUserInformation( 'wl_prof_read', 'wl_prof_read_password')
        professor_write_user = DAM.DatabaseUserInformation( 'wl_prof_write', 'wl_prof_write_password')
        self.professor_credentials = { NAME  : PROFESSOR, READ  : professor_read_user, WRITE : professor_write_user }

        administrator_read_user = DAM.DatabaseUserInformation( 'wl_admin_read', 'wl_admin_read_password')
        administrator_write_user = DAM.DatabaseUserInformation( 'wl_admin_write', 'wl_admin_write_password' )
        self.administrator_credentials = { NAME  : ADMINISTRATOR, READ  : administrator_read_user, WRITE : administrator_write_user }

        external_read_user = DAM.DatabaseUserInformation( 'wl_exter_read', 'wl_exter_read_password')
        external_write_user = DAM.DatabaseUserInformation( 'wl_exter_write', 'wl_exter_write_password')
        self.external_credentials = { NAME  : EXTERNAL_ENTITY, READ  : external_read_user, WRITE : external_write_user }

        # This super_administrator doesn't exist in weblab, it's just
        # the user that can enter commands directly into the DB
        super_administrator_read_user = DAM.DatabaseUserInformation( 'wl_administrator', 'wl_administrator_password' )
        super_administrator_write_user = DAM.DatabaseUserInformation( 'wl_administrator', 'wl_administrator_password' )
        self.super_administrator_credentials = { NAME  : "r00t", READ  : super_administrator_read_user, WRITE : super_administrator_write_user }

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.gateway = DatabaseGateway.create_gateway(cfg_manager)
        self.gateway._execute(
                    self.super_administrator_credentials,
                    "DELETE FROM wl_UserUsedExperiment"
                )
        
    def test_get_user_by_name(self):

        my_get_user_by_name = DatabaseMySQLGateway._db_credentials_checker(
                DatabaseMySQLGateway.DatabaseGateway._get_user_by_name
            )

        student = my_get_user_by_name(
                self.gateway,
                self.student_credentials,
                'student2'
            )

        self.assertEquals(
                student.login,
                'student2'
            )
        self.assertEquals(
                student.full_name,
                'Name of student 2'
            )
    
        self.assertRaises(
            DbExceptions.DbProvidedUserNotFoundException,
            my_get_user_by_name,
            self.gateway,
            self.student_credentials,
            'studentXX'
        )

    def test_list_experiments(self):
        student = self.gateway.get_user_by_name(
                self.student_credentials,
                'student1'
            )
        student2 = self.gateway.get_user_by_name(
                self.student_credentials,
                'student2'
            )
        
        experiments = self.gateway.list_experiments(
                self.student_credentials,
                student.id
            )

        self.assertEquals(
                len(experiments),
                5
            )

        experiments = self.gateway.list_experiments(
                self.student_credentials,
                student2.id
            )

        self.assertEquals(
                len(experiments),
                7
            )

        experiment_names =list( ( experiment.experiment.name for experiment in experiments ))

        self.assertTrue( 'ud-fpga' in experiment_names )
        self.assertTrue( 'ud-pld' in experiment_names )
        self.assertTrue( 'ud-gpib' in experiment_names )

    def test_get_groups_of_user(self):
        user_id = self.gateway.get_user_by_name( self.student_credentials, "prof1" ).id
        groups = self.gateway.get_groups_of_user(
                self.professor_credentials, 
                user_id
            )
        self.assertEquals(
                len(groups),
                1
            )
        group = groups[0]
        self.assertEquals(
                group.name,
                "professors1and2"
            )
        self.assertEquals(
                group.owner.full_name,
                "Name of administrator 1"
            )
        self.assertEquals(
                group.owner.email,
                "weblab@deusto.es"
            )

    def test_get_groups_of_group(self):
        user_id = self.gateway.get_user_by_name( self.student_credentials, "prof1" ).id
        groups = self.gateway.get_groups_of_user(
                self.professor_credentials, 
                user_id
            )
        self.assertEquals(
                len(groups),
                1
            )
        group = groups[0]
        self.assertEquals(
                group.name,
                "professors1and2"
            )
        # Now
        groups = self.gateway.get_groups_of_group(
                self.professor_credentials,
                group.id
            )
        self.assertEquals(
                len(groups),
                1
            )
        group = groups[0]
        self.assertEquals(
                group.name,
                "groups_professors1and2_and_professor3"
            )
        self.assertEquals(
                group.owner.login,
                "admin1"
            )

    def test_get_all_groups_of_group(self):
        user_id = self.gateway.get_user_by_name( self.student_credentials, "prof1" ).id
        groups = self.gateway.get_groups_of_user(
                self.professor_credentials, 
                user_id
            )
        self.assertEquals(
                len(groups),
                1
            )
        group = groups[0]
        self.assertEquals(
                group.name,
                "professors1and2"
            )


        # Now
        my_get_all_groups_of_group = DatabaseMySQLGateway._db_credentials_checker(
                DatabaseMySQLGateway.DatabaseGateway._get_all_groups_of_group
            )

        groups = my_get_all_groups_of_group(
                self.gateway,
                self.professor_credentials,
                group.id
            )
        self.assertEquals(
                len(groups),
                1
            )
        group = groups[0]
        self.assertEquals(
                group.name,
                "groups_professors1and2_and_professor3"
            )
        self.assertEquals(
                group.owner.login,
                "admin1"
            )

    def test_get_all_groups_of_user(self):
        user_id = self.gateway.get_user_by_name( self.student_credentials, "prof1" ).id
        # Now
        my_get_all_groups_of_user = DatabaseMySQLGateway._db_credentials_checker(
                DatabaseMySQLGateway.DatabaseGateway._get_all_groups_of_user
            )

        groups = my_get_all_groups_of_user(
                self.gateway,
                self.professor_credentials,
                user_id
            )
        self.assertEquals(
                len(groups),
                2
            )

        group = groups[0]
        self.assertEquals(
                group.name,
                "professors1and2"
            )
        self.assertEquals(
                group.owner.full_name,
                "Name of administrator 1"
            )
        self.assertEquals(
                group.owner.email,
                "weblab@deusto.es"
            )


        group = groups[1]
        self.assertEquals(
                group.name,
                "groups_professors1and2_and_professor3"
            )
        self.assertEquals(
                group.owner.login,
                "admin1"
            )

        other_user = self.gateway.get_user_by_name(
                self.student_credentials,
                'student2'
            )

        groups = my_get_all_groups_of_user(
                self.gateway,
                self.student_credentials,
                other_user.id
            )

    def test_retrieve_user_permissions(self):
        user_id = self.gateway.get_user_by_name( self.student_credentials, "student2" ).id

        my_retrieve_user_permissions = DatabaseMySQLGateway._db_credentials_checker(
                DatabaseMySQLGateway.DatabaseGateway._retrieve_user_permissions
            )

        permissions = my_retrieve_user_permissions(
                self.gateway,
                self.student_credentials,
                user_id,
                'experiment_allowed'
            )

        pld_permissions = [ perm for perm in permissions if perm.parameters['experiment_permanent_id'].value == 'ud-pld']
        self.assertEquals(1, len(pld_permissions) )

        first_permission            = pld_permissions[0]
        first_permission_parameters = first_permission.parameters
        first_permission_type       = first_permission.permission_type
        first_permission_owner      = first_permission.owner
        
        self.assertEquals(
                len(first_permission_parameters),
                3
            )
        self.assertEquals(
                first_permission_parameters['experiment_permanent_id'].value,
                'ud-pld'
            )

        self.assertEquals(
                first_permission_parameters['experiment_category_id'].value,
                'PLD experiments'
            )

        self.assertEquals(
                first_permission_parameters['time_allowed'].value,
                '100'
            )

        self.assertEquals(
                self.gateway._get_float_parameter_from_permission(
                    first_permission,
                    'time_allowed'
                ),
                100.0
            )

        self.assertRaises(
                DbExceptions.InvalidPermissionParameterFormatException,
                self.gateway._get_float_parameter_from_permission,
                first_permission,
                'experiment_permanent_id'
            )
                
        self.assertEquals(
                first_permission_owner.login,
                'prof1'
            )
        self.assertEquals(
                first_permission_type.name,
                'experiment_allowed'
            )

        gpib_permissions = [ perm for perm in permissions if perm.parameters['experiment_permanent_id'].value == 'ud-gpib']
        self.assertEquals(1, len(gpib_permissions) )

        second_permission            = gpib_permissions[0]
        second_permission_parameters = second_permission.parameters
        second_permission_type       = second_permission.permission_type
        second_permission_owner      = second_permission.owner
        
        self.assertEquals(
                len(second_permission_parameters),
                3
            )
        self.assertEquals(
                second_permission_parameters['experiment_permanent_id'].value,
                'ud-gpib'
            )
        self.assertEquals(
                second_permission_parameters['experiment_category_id'].value,
                'GPIB experiments'
            )
        self.assertEquals(
                second_permission_parameters['time_allowed'].value,
                '150'
            )
        self.assertEquals(
                second_permission_owner.login,
                'prof1'
            )
        self.assertEquals(
                second_permission_type.name,
                'experiment_allowed'
            )

        self.assertEquals(
                first_permission_type,
                second_permission_type
            )
        
        self.assertEquals(
                first_permission_parameters['experiment_permanent_id'].parameter_type,
                second_permission_parameters['experiment_permanent_id'].parameter_type,
            )
        self.assertEquals(
                second_permission_parameters['experiment_permanent_id'].parameter_type.name,
                'experiment_permanent_id'
            )
        self.assertEquals(
                second_permission_parameters['experiment_permanent_id'].parameter_type.type,
                'string'
            )

    def test_retrieve_group_permissions(self):
        user_id = self.gateway.get_user_by_name( self.student_credentials, "student2" ).id

        groups = self.gateway.get_groups_of_user(
                self.professor_credentials, 
                user_id
            )

        self.assertEquals(
                len(groups),
                1
            )
        self.assertEquals(
                groups[0].name,
                '5A'
            )
        group_id = groups[0].id

        my_retrieve_group_permissions = DatabaseMySQLGateway._db_credentials_checker(
                DatabaseMySQLGateway.DatabaseGateway._retrieve_group_permissions
            )

        permissions = my_retrieve_group_permissions(
                self.gateway,
                self.student_credentials,
                group_id,
                'experiment_allowed'
            )

        fpga_permissions = [ perm for perm in permissions if perm.parameters['experiment_permanent_id'].value == 'ud-fpga']

        self.assertEquals(1, len(fpga_permissions) )

        first_permission            = fpga_permissions[0]
        first_permission_parameters = first_permission.parameters
        first_permission_type       = first_permission.permission_type
        first_permission_owner      = first_permission.owner
        
        self.assertEquals(
                len(first_permission_parameters),
                3
            )
        self.assertEquals(
                first_permission_parameters['experiment_permanent_id'].value,
                'ud-fpga'
            )

        self.assertEquals(
                first_permission_parameters['time_allowed'].value,
                '30'
            )

        self.assertEquals(
                first_permission_parameters['experiment_category_id'].value,
                'FPGA experiments'
            )


        self.assertEquals(
                first_permission_owner.login,
                'prof1'
            )
        self.assertEquals(
                first_permission_type.name,
                'experiment_allowed'
            )

        self.assertEquals(
                first_permission_parameters['experiment_permanent_id'].parameter_type.name,
                'experiment_permanent_id'
            )
        self.assertEquals(
                first_permission_parameters['experiment_permanent_id'].parameter_type.type,
                'string'
            )

    def test_retrieve_experiment(self):
        my_retrieve_experiment = DatabaseMySQLGateway._db_credentials_checker(
                DatabaseMySQLGateway.DatabaseGateway._retrieve_experiment
            )
        experiment = my_retrieve_experiment(
                self.gateway, 
                self.student_credentials,
                "PLD experiments",
                "ud-pld"
            )
        self.assertEquals(
                "ud-pld",
                experiment.name
            )
        self.assertEquals(
                "PLD experiments",
                experiment.category.name
            )
        self.assertEquals(
                "prof1",
                experiment.owner.login
            )
        self.assertEquals(
                "weblab@deusto.es",
                experiment.owner.email
            )
        self.assertRaises(
                DbExceptions.DbProvidedExperimentNotFoundException,
                my_retrieve_experiment,
                self.gateway,
                self.student_credentials,
                "PLD experiments",
                "this does not exist"
            )
        self.assertRaises(
                DbExceptions.DbProvidedExperimentNotFoundException,
                my_retrieve_experiment,
                self.gateway,
                self.student_credentials,
                "this does not exist",
                "ud-pld"
            )

    def test_store_and_list_usages_per_user(self):
        student = self.gateway.get_user_by_name(
                self.student_credentials,
                'student1'
            )

        initial_usage = Usage.ExperimentUsage()
        initial_usage.start_date     = time.time()
        initial_usage.end_date       = time.time()
        initial_usage.from_ip        = "130.206.138.16"
        initial_usage.experiment_id  = ExperimentId.ExperimentId("ud-dummy","Dummy experiments")
        initial_usage.coord_address  = CoordAddress.CoordAddress("machine1","instance1","server1")

        file1    = Usage.FileSent(
                'path/to/file1',
                '{sha}12345',
                time.time()
            )

        file2    = Usage.FileSent(
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

        self.gateway.store_experiment_usage(
                self.student_credentials,
                student.id,
                initial_usage
            )

        number, usages = self.gateway.list_usages_per_user(
                self.student_credentials,
                student.id,
                0
            )

        self.assertEquals( 1, number )
        self.assertEquals( 1, len(usages) )
        usage = usages[0]

        self.assertEquals( initial_usage.start_date,     usage.start_date)
        self.assertEquals( initial_usage.end_date,       usage.end_date)
        self.assertEquals( initial_usage.from_ip,        usage.from_ip)
        self.assertEquals( initial_usage.experiment_id,  usage.experiment_id)
        self.assertEquals( initial_usage.coord_address,  usage.coord_address)

        full_usage = self.gateway.retrieve_usage(
            self.student_credentials,
            student.id,
            usage.experiment_usage_id
        )

        self.assertEquals( initial_usage.start_date,     full_usage.start_date)
        self.assertEquals( initial_usage.end_date,       full_usage.end_date  )
        self.assertEquals( initial_usage.from_ip,        full_usage.from_ip   )
        self.assertEquals( initial_usage.experiment_id,  full_usage.experiment_id)
        self.assertEquals( initial_usage.coord_address,  full_usage.coord_address)

        self.assertEquals( 2, len(full_usage.commands) )
        self.assertEquals( command1.command,          full_usage.commands[0].command)
        self.assertEquals( command1.timestamp_before, full_usage.commands[0].timestamp_before)
        self.assertEquals( command1.response,          full_usage.commands[0].response)
        self.assertEquals( command1.timestamp_after,  full_usage.commands[0].timestamp_after)
        
        self.assertEquals( command2.command,          full_usage.commands[1].command)
        self.assertEquals( command2.timestamp_before, full_usage.commands[1].timestamp_before)
        self.assertEquals( command2.response,         full_usage.commands[1].response)
        self.assertEquals( command2.timestamp_after, full_usage.commands[1].timestamp_after)

        self.assertEquals( 2, len(full_usage.sent_files) )

        self.assertEquals( file1.file_sent,        full_usage.sent_files[0].file_sent)
        self.assertEquals( file1.file_hash,        full_usage.sent_files[0].file_hash)
        self.assertEquals( file1.file_info,        full_usage.sent_files[0].file_info)
        self.assertEquals( file1.timestamp_before, full_usage.sent_files[0].timestamp_before)
        self.assertEquals( file1.response,         full_usage.sent_files[0].response)
        self.assertEquals( file1.timestamp_after,  full_usage.sent_files[0].timestamp_after)

        self.assertEquals( file2.file_sent,        full_usage.sent_files[1].file_sent)
        self.assertEquals( file2.file_hash,        full_usage.sent_files[1].file_hash)
        self.assertEquals( file2.file_info,        full_usage.sent_files[1].file_info)
        self.assertEquals( file2.timestamp_before, full_usage.sent_files[1].timestamp_before)
        self.assertEquals( file2.response,         full_usage.sent_files[1].response)
        self.assertEquals( file2.timestamp_after,  full_usage.sent_files[1].timestamp_after)

def suite():
    return unittest.makeSuite(DatabaseMySQLGatewayTestCase)

if __name__ == '__main__':
    unittest.main()

