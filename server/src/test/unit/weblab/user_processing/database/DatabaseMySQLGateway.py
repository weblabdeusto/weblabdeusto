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
    """Note: Methods tested from UserProcessingServer won't be tested again here."""

    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.gateway = DatabaseGateway.create_gateway(cfg_manager)
        self.gateway._delete_all_uses()
    
    def test_get_user_by_name(self):
        self.assertRaises(
            DbExceptions.DbProvidedUserNotFoundException,
            self.gateway.get_user_by_name,
            'studentXX'
        )        

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
        
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, initial_usage)

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

        # Dummy (Group Permissions)
        dummy_permissions = [ perm for perm in permissions if perm.get_parameter("experiment_permanent_id").value == "ud-dummy"]
        self.assertEquals(1, len(dummy_permissions) )

        fpga_permission = dummy_permissions[0]
        self.assertEquals(len(fpga_permission.parameters), 3)
        self.assertEquals(fpga_permission.get_parameter('experiment_permanent_id').value, 'ud-dummy')
        self.assertEquals(fpga_permission.get_parameter('experiment_category_id').value, 'Dummy experiments')
        self.assertEquals(fpga_permission.get_parameter('time_allowed').value, '150')
        self.assertEquals(fpga_permission.get_permission_type().name, 'experiment_allowed')
        self.assertEquals(fpga_permission.get_parameter('experiment_permanent_id').get_name(), 'experiment_permanent_id')
        self.assertEquals(fpga_permission.get_parameter('experiment_permanent_id').get_datatype(), 'string')   
            
        experiments = self.gateway.get_experiments(student2.login)
        self.assertEquals(len(experiments), 0)

    def test_get_experiment_uses(self):
        student2 = self.gateway.get_user_by_name('student2')
        from_date = datetime.datetime.utcnow()
        to_date = datetime.datetime.utcnow()
        group_id = 1
        experiment_id = 1
        
        self.gateway._insert_user_used_experiment("student2", "ud-fpga", "FPGA experiments", time.time(), "unknown", "fpga:process1@scabb", '8', time.time())
        self.gateway._insert_ee_used_experiment("ee1", "ud-dummy", "Dummy experiments", time.time(), "unknown", "dummy:process1@plunder", '9', time.time())
        
        experiment_uses = self.gateway.get_experiment_uses(student2.login, from_date, to_date, group_id, experiment_id)
        self.assertEquals(len(experiment_uses), 0)

    def test_get_experiment_uses_with_null_params(self):
        student2 = self.gateway.get_user_by_name('student2')
        from_date = None
        to_date = None
        group_id = None
        experiment_id = None
        
        self.gateway._insert_user_used_experiment("student2", "ud-fpga", "FPGA experiments", time.time(), "unknown", "fpga:process1@scabb", '5', time.time())
        self.gateway._insert_ee_used_experiment("ee1", "ud-dummy", "Dummy experiments", time.time(), "unknown", "dummy:process1@plunder", '6', time.time())
        
        experiment_uses = self.gateway.get_experiment_uses(student2.login, from_date, to_date, group_id, experiment_id)
        self.assertEquals(len(experiment_uses), 0)

        
def suite():
    return unittest.makeSuite(DatabaseMySQLGatewayTestCase)

if __name__ == '__main__':
    unittest.main()
