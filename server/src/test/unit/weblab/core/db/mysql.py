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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#

import unittest
import time
import datetime

import test.unit.configuration as configuration

import voodoo.configuration as ConfigurationManager

import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.core.db.gateway as DatabaseGateway

from weblab.data.experiments import ExperimentUsage, CommandSent, FileSent
from weblab.data.experiments import ExperimentId
import weblab.data.command as Command

import weblab.db.exc as DbExceptions

def create_usage(gateway, reservation_id = 'my_reservation_id'):
        session = gateway.Session()
        student1 = gateway._get_user(session, 'student1')

        initial_usage = ExperimentUsage()
        initial_usage.start_date    = time.time()
        initial_usage.end_date      = time.time()
        initial_usage.from_ip       = "130.206.138.16"
        initial_usage.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        initial_usage.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        initial_usage.reservation_id = reservation_id

        file1 = FileSent(
                    'path/to/file1',
                    '{sha}12345',
                    time.time()
            )
        
        file2 = FileSent(
                    'path/to/file2',
                    '{sha}123456',
                    time.time(),
                    Command.Command('response'),
                    time.time(),
                    file_info = 'program'
            )

        command1 = CommandSent(
                    Command.Command("your command1"),
                    time.time()
            )
        
        command2 = CommandSent(
                    Command.Command("your command2"),
                    time.time(),
                    Command.Command("your response2"),
                    time.time()
            )

        initial_usage.append_command(command1)
        initial_usage.append_command(command2)
        initial_usage.append_file(file1)
        initial_usage.append_file(file2)
        
        gateway.store_experiment_usage(student1.login, {'facebook' : False}, initial_usage)
        return student1, initial_usage, command1, command2, file1, file2

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

    def test_is_access_forward(self):
        self.assertFalse( self.gateway.is_access_forward('student1') )
        self.assertTrue( self.gateway.is_access_forward('any') )

    def test_store_experiment_usage(self):
        student1, initial_usage, command1, command2, file1, file2 = create_usage(self.gateway)

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
       

    def test_add_command(self):
        session = self.gateway.Session()
        student1 = self.gateway._get_user(session, 'student1')

        RESERVATION_ID1 = 'my_reservation_id1'
        RESERVATION_ID2 = 'my_reservation_id2'

        usage1 = ExperimentUsage()
        usage1.start_date    = time.time()
        usage1.end_date      = time.time()
        usage1.from_ip       = "130.206.138.16"
        usage1.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage1.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage1.reservation_id = RESERVATION_ID1
        
        command1 = CommandSent(
                    Command.Command("your command1"),
                    time.time(),
                    Command.Command("your response1"),
                    time.time()
            )

        usage1.append_command(command1)

        usage2 = ExperimentUsage()
        usage2.start_date    = time.time()
        usage2.end_date      = time.time()
        usage2.from_ip       = "130.206.138.17"
        usage2.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage2.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage2.reservation_id = RESERVATION_ID2
        
        command2 = CommandSent(
                    Command.Command("your command2"),
                    time.time(),
                    Command.Command("your response2"),
                    time.time()
            )

        usage2.append_command(command2)
       
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage1)
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage2)

        batch_command = CommandSent(
                    Command.Command("@@@batch@@@"),
                    time.time(),
                    Command.Command("batch"),
                    time.time()
            )

        finishing_command = CommandSent(
                    Command.Command("@@@finish@@@"),
                    time.time(),
                    Command.Command("finish"),
                    time.time()
            )

        usages = self.gateway.list_usages_per_user(student1.login)
        self.assertEquals(2, len(usages))

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(1, len(full_usage1.commands))
        self.assertEquals(1, len(full_usage2.commands))

        self.gateway.append_command(RESERVATION_ID1, batch_command)
        self.gateway.append_command(RESERVATION_ID2, finishing_command)

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(2, len(full_usage1.commands))
        self.assertEquals(2, len(full_usage2.commands))

        self.assertEquals("@@@batch@@@", full_usage1.commands[1].command.commandstring)
        self.assertEquals("batch",       full_usage1.commands[1].response.commandstring)

        self.assertEquals("@@@finish@@@", full_usage2.commands[1].command.commandstring)
        self.assertEquals("finish",       full_usage2.commands[1].response.commandstring)

    def test_update_command(self):
        session = self.gateway.Session()
        student1 = self.gateway._get_user(session, 'student1')

        RESERVATION_ID1 = 'my_reservation_id1'

        usage1 = ExperimentUsage()
        usage1.start_date    = time.time()
        usage1.end_date      = time.time()
        usage1.from_ip       = "130.206.138.16"
        usage1.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage1.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage1.reservation_id = RESERVATION_ID1

        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage1)

        usages = self.gateway.list_usages_per_user(student1.login)
        self.assertEquals(1, len(usages))

        full_usage = self.gateway.retrieve_usage(usages[0].experiment_use_id)

        self.assertEquals(0, len(full_usage.commands))

        command1 = CommandSent( Command.Command("your command"), time.time() )
        command_id = self.gateway.append_command( RESERVATION_ID1, command1 )

        full_usage = self.gateway.retrieve_usage(usages[0].experiment_use_id)

        self.assertEquals("your command",        full_usage.commands[0].command.commandstring)
        self.assertEquals(Command.NullCommand(), full_usage.commands[0].response)

        self.gateway.update_command(command_id, Command.Command("the response"), time.time())

        full_usage = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        self.assertEquals("your command",      full_usage.commands[0].command.commandstring)
        self.assertEquals("the response",      full_usage.commands[0].response.commandstring)


    def test_finish_experiment_usage(self):
        session = self.gateway.Session()
        student1 = self.gateway._get_user(session, 'student1')

        RESERVATION_ID1 = 'my_reservation_id1'
        RESERVATION_ID2 = 'my_reservation_id2'

        usage1 = ExperimentUsage()
        usage1.start_date    = time.time()
        usage1.from_ip       = "130.206.138.16"
        usage1.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage1.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage1.reservation_id = RESERVATION_ID1
        
        command1 = CommandSent(
                    Command.Command("your command1"),
                    time.time(),
                    Command.Command("your response1"),
                    time.time()
            )

        usage1.append_command(command1)

        usage2 = ExperimentUsage()
        usage2.start_date    = time.time()
        usage2.from_ip       = "130.206.138.17"
        usage2.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage2.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage2.reservation_id = RESERVATION_ID2
        
        command2 = CommandSent(
                    Command.Command("your command2"),
                    time.time(),
                    Command.Command("your response2"),
                    time.time()
            )

        usage2.append_command(command2)
       
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage1)
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage2)

        finishing_command = CommandSent(
                    Command.Command("@@@finish@@@"),
                    time.time(),
                    Command.Command("finish"),
                    time.time()
            )

        usages = self.gateway.list_usages_per_user(student1.login)
        self.assertEquals(2, len(usages))

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(None, full_usage1.end_date)
        self.assertEquals(None, full_usage2.end_date)

        self.assertEquals(1, len(full_usage1.commands))
        self.assertEquals(1, len(full_usage2.commands))

        result = self.gateway.finish_experiment_usage(RESERVATION_ID1, time.time(), finishing_command)

        self.assertTrue(result)

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertNotEqual(None, full_usage1.end_date)
        self.assertEquals(None, full_usage2.end_date)

        self.assertEquals(2, len(full_usage1.commands))
        self.assertEquals(1, len(full_usage2.commands))

        self.assertEquals("@@@finish@@@", full_usage1.commands[1].command.commandstring)
        self.assertEquals("finish",       full_usage1.commands[1].response.commandstring)


    def test_add_file(self):
        session = self.gateway.Session()
        student1 = self.gateway._get_user(session, 'student1')

        RESERVATION_ID1 = 'my_reservation_id1'
        RESERVATION_ID2 = 'my_reservation_id2'

        usage1 = ExperimentUsage()
        usage1.start_date    = time.time()
        usage1.end_date      = time.time()
        usage1.from_ip       = "130.206.138.16"
        usage1.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage1.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage1.reservation_id = RESERVATION_ID1
        
        command1 = CommandSent(
                    Command.Command("your command1"),
                    time.time(),
                    Command.Command("your response1"),
                    time.time()
            )

        usage1.append_command(command1)

        usage2 = ExperimentUsage()
        usage2.start_date    = time.time()
        usage2.end_date      = time.time()
        usage2.from_ip       = "130.206.138.17"
        usage2.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage2.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage2.reservation_id = RESERVATION_ID2
        
        command2 = CommandSent(
                    Command.Command("your command2"),
                    time.time(),
                    Command.Command("your response2"),
                    time.time()
            )

        usage2.append_command(command2)
       
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage1)
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage2)

        file_sent1 = FileSent(
                    'path/to/file2',
                    '{sha}123456',
                    time.time(),
                    Command.Command('response'),
                    time.time(),
                    file_info = 'program'
            )

        usages = self.gateway.list_usages_per_user(student1.login)
        self.assertEquals(2, len(usages))

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(1, len(full_usage1.commands))
        self.assertEquals(1, len(full_usage2.commands))
        self.assertEquals(0, len(full_usage1.sent_files))
        self.assertEquals(0, len(full_usage2.sent_files))

        self.gateway.append_file(RESERVATION_ID1, file_sent1)

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(1, len(full_usage1.commands))
        self.assertEquals(1, len(full_usage2.commands))
        self.assertEquals(1, len(full_usage1.sent_files))
        self.assertEquals(0, len(full_usage2.sent_files))

        self.assertEquals("response",       full_usage1.sent_files[0].response.commandstring)

    def test_update_file(self):
        session = self.gateway.Session()
        student1 = self.gateway._get_user(session, 'student1')

        RESERVATION_ID1 = 'my_reservation_id1'
        RESERVATION_ID2 = 'my_reservation_id2'

        usage1 = ExperimentUsage()
        usage1.start_date    = time.time()
        usage1.end_date      = time.time()
        usage1.from_ip       = "130.206.138.16"
        usage1.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage1.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage1.reservation_id = RESERVATION_ID1
        
        usage2 = ExperimentUsage()
        usage2.start_date    = time.time()
        usage2.end_date      = time.time()
        usage2.from_ip       = "130.206.138.17"
        usage2.experiment_id = ExperimentId("ud-dummy","Dummy experiments")
        usage2.coord_address = CoordAddress.CoordAddress("machine1","instance1","server1") #.translate_address("server1:instance1@machine1")
        usage2.reservation_id = RESERVATION_ID2
        
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage1)
        self.gateway.store_experiment_usage(student1.login, {'facebook' : False}, usage2)

        file_sent1 = FileSent(
                    'path/to/file2',
                    '{sha}123456',
                    time.time(),
                    file_info = 'program'
            )

        usages = self.gateway.list_usages_per_user(student1.login)
        self.assertEquals(2, len(usages))

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(0, len(full_usage1.commands))
        self.assertEquals(0, len(full_usage2.commands))
        self.assertEquals(0, len(full_usage1.sent_files))
        self.assertEquals(0, len(full_usage2.sent_files))

        file_sent_id = self.gateway.append_file(RESERVATION_ID1, file_sent1)

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(0, len(full_usage1.commands))
        self.assertEquals(0, len(full_usage2.commands))
        self.assertEquals(1, len(full_usage1.sent_files))
        self.assertEquals(0, len(full_usage2.sent_files))

        self.assertEquals(None,       full_usage1.sent_files[0].response.commandstring)

        self.gateway.update_file(file_sent_id, Command.Command("response"), time.time())

        full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
        full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)

        self.assertEquals(0, len(full_usage1.commands))
        self.assertEquals(0, len(full_usage2.commands))
        self.assertEquals(1, len(full_usage1.sent_files))
        self.assertEquals(0, len(full_usage2.sent_files))

        self.assertEquals("response",       full_usage1.sent_files[0].response.commandstring)

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
        
    def test_get_groups(self):
        self.gateway._insert_group("TestGroup", None)
        groups = self.gateway.get_groups('student1', None)
        self.assertTrue(len(groups) > 1)
        
    def test_get_groups_filtering_by_parent(self):
        testgroup = self.gateway._insert_group("TestGroup", None)
        g1 = self.gateway._insert_group("ChildOfTestGroup1", testgroup)
        g2 = self.gateway._insert_group("ChildOfTestGroup2", testgroup)
        
        groups = self.gateway.get_groups('student1', testgroup)
        for g in groups:
            self.assertTrue(g in (g1, g2,))
        

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
