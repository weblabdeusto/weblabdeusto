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

import weblab.data.Command as Command

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.locator.EasyLocator as EasyLocator

import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.laboratory.LaboratoryServer as LaboratoryServer
import weblab.laboratory.IsUpAndRunningHandler as IsUpAndRunningHandler

import weblab.exceptions.laboratory.LaboratoryExceptions as LaboratoryExceptions

import weblab.methods as weblab_methods

import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId

import FakeUrllib2
import FakeSocket
import time

# 
# In this file you'll find three test cases:
# 
#  * LaboratoryServerLoadingTestCase: testing the configuration parsing
#  * LaboratoryServerManagementTestCase: testing the management of reserves
#              and experiments
#  * LaboratoryServerSendingTestCase: testing the interaction with 
#              experiment servers
# 
# Take into account that each test case relies on the previous test 
# case. If LaboratoryServerLoadingTestCase fails, the rest might fail.
# If LaboratoryServerManagementTestCase fails, LaboratoryServerSendingTestCase
# might fail.
# 
# Additionally, you'll find two fake objects, used by the test cases.
# 


###################################################################
# 
#   T E S T     C A S E S 
# 
# 

################################################
# 
# This TestCase test the configuration parsing
# performed by the LaboratoryServer
# 
class LaboratoryServerLoadingTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.locator        = EasyLocator.EasyLocator(
                    CoordAddress.CoordAddress('mach','inst','serv'),
                    FakeLocator((FakeClient(),))
                )

        self.experiment_instance_id = ExperimentInstanceId.ExperimentInstanceId("exp_inst","exp_name","exp_cat")

    def test_correct_single_instance(self):
        self.cfg_manager._set_value(LaboratoryServer.WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS,
                { 'exp_inst:exp_name@exp_cat': { 'coord_address': 'myserver:myinstance@mymachine',
                                                 'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                               ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )} })

        self.lab = LaboratoryServer.LaboratoryServer( None, self.locator, self.cfg_manager )

    def test_correct_two_instances(self):
        self.cfg_manager._set_value(LaboratoryServer.WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS,
                { 'exp_inst:exp_name1@exp_cat1': { 'coord_address': 'myserver1:myinstance@mymachine',
                                                   'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",) ),
                                                                 ('HostIsUpAndRunningHandler', ("hostname",), {'port': 80}), )},
                  'exp_inst:exp_name2@exp_cat2': { 'coord_address': 'myserver2:myinstance@mymachine',
                                                   'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",) ), ) } })

        self.lab = LaboratoryServer.LaboratoryServer( None, self.locator, self.cfg_manager )

    def test_wrong_coordaddress_format(self):
        self.cfg_manager._set_value(LaboratoryServer.WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS,
                { 'exp_inst:exp_name1@exp_cat1': { 'coord_address': 'myserver1:myinstance@mymachine',
                                                   'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                                 ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )},
                  'exp_inst:exp_name2@exp_cat2': { 'coord_address': 'myserver2:myinstancemymachine',
                                                   'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                                 ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )} })

        self.assertRaises( LaboratoryExceptions.InvalidLaboratoryConfigurationException,
                            LaboratoryServer.LaboratoryServer,
                            None, self.locator, self.cfg_manager )

    def test_wrong_invalid_format(self):
        self.cfg_manager._set_value(LaboratoryServer.WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS,
                { 'exp_inst:exp_name1exp_cat1': { 'coord_address': 'myserver1:myinstance@mymachine',
                                                  'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                                ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )},
                  'exp_inst:exp_name2@exp_cat2': { 'coord_address': 'myserver2:myinstance@mymachine',
                                                   'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                                 ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )} })

        self.assertRaises( LaboratoryExceptions.InvalidLaboratoryConfigurationException,
                            LaboratoryServer.LaboratoryServer,
                            None, self.locator, self.cfg_manager )
        
#####################################################
# 
# This TestCase test the management of experiments.
# It relies on the previous testcase.
# 
class LaboratoryServerManagementTestCase(unittest.TestCase):

    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        self.fake_client  = FakeClient()
        self.fake_locator = FakeLocator((self.fake_client, ))
        locator        = EasyLocator.EasyLocator(
                    CoordAddress.CoordAddress('mach','inst','serv'),
                    self.fake_locator
                )

        self.experiment_instance_id = ExperimentInstanceId.ExperimentInstanceId("exp_inst","exp_name","exp_cat")
        self.experiment_coord_address = CoordAddress.CoordAddress.translate_address('myserver:myinstance@mymachine')

        cfg_manager._set_value('laboratory_assigned_experiments',
                            { 'exp_inst:exp_name@exp_cat': { 'coord_address': 'myserver:myinstance@mymachine',
                                                             'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                                           ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )} })

        self.lab = LaboratoryServer.LaboratoryServer(
                None,
                locator,
                cfg_manager
            )

    def test_reserve_experiment_instance_id_simple(self):
        self.assertEquals(0, self.fake_client.started)
        self.assertEquals(0, self.fake_client.disposed)

        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        self.assertEquals(1, self.fake_client.started)
        self.assertEquals(0, self.fake_client.disposed)

        self.lab.do_free_experiment(lab_session_id)
        self.assertEquals(1, self.fake_client.started)
        self.assertEquals(1, self.fake_client.disposed)
        
    def test_resolve_experiment_address(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        exp_coord_address = self.lab.do_resolve_experiment_address(lab_session_id)
        self.assertEquals(self.experiment_coord_address, exp_coord_address)

    def test_reserve_experiment_instance_id_already_used(self):

        self.assertEquals(0, self.fake_client.started)
        self.assertEquals(0, self.fake_client.disposed)

        lab_session_id1 = self.lab.do_reserve_experiment(self.experiment_instance_id)

        self.assertEquals(1, self.fake_client.started)
        self.assertEquals(0, self.fake_client.disposed)

        lab_session_id2 = self.lab.do_reserve_experiment(self.experiment_instance_id)

        self.assertEquals(2, self.fake_client.started)
        self.assertEquals(1, self.fake_client.disposed)

        # The new reservation has overriden the old one, which doesn't
        # exist anymore
        self.assertRaises(
                LaboratoryExceptions.SessionNotFoundInLaboratoryServerException,
                self.lab.do_send_command,
                lab_session_id1,
                'foo'
            )

        lab_session_id3 = self.lab.do_reserve_experiment(self.experiment_instance_id)

        # Again
        self.assertRaises(
                LaboratoryExceptions.SessionNotFoundInLaboratoryServerException,
                self.lab.do_send_command,
                lab_session_id2,
                'foo'
            )

        self.assertEquals(3, self.fake_client.started)
        self.assertEquals(2, self.fake_client.disposed)

        self.lab.do_free_experiment(lab_session_id3)

        self.assertEquals(3, self.fake_client.started)
        self.assertEquals(3, self.fake_client.disposed)
        
    def _fake_is_up_and_running_handlers(self):
        FakeUrllib2.reset()
        FakeSocket.reset()
        exp_handler = self.lab._assigned_experiments._retrieve_experiment_handler(self.experiment_instance_id)
        exp_handler.is_up_and_running_handlers[0]._urllib2 = FakeUrllib2
        exp_handler.is_up_and_running_handlers[1]._socket = FakeSocket   
        
    def test_check_experiments_resources(self):
        self._fake_is_up_and_running_handlers()
        failing_experiment_instance_ids = self.lab.do_check_experiments_resources()
        self.assertEquals(0, len(failing_experiment_instance_ids))

    def test_check_experiments_resources_handler_failed(self):
        self._fake_is_up_and_running_handlers()
        FakeUrllib2.expected_action = FakeUrllib2.HTTP_BAD_CONTENT
        failing_experiment_instance_ids = self.lab.do_check_experiments_resources()
        self.assertEquals(1, len(failing_experiment_instance_ids))
        self.assertTrue(self.experiment_instance_id in failing_experiment_instance_ids)
        fails = failing_experiment_instance_ids[self.experiment_instance_id]
        self.assertEquals(IsUpAndRunningHandler.WebcamIsUpAndRunningHandler.DEFAULT_TIMES - 1, fails.count('; '))

    def test_check_experiments_resources_test_me_failed(self):
        self._fake_is_up_and_running_handlers()
        message = "fail asking for a server"
        self.fake_locator.fail_on_server_request = message
        failing_experiment_instance_ids = self.lab.do_check_experiments_resources()
        self.assertEquals(1, len(failing_experiment_instance_ids))
        self.assertTrue(self.experiment_instance_id in failing_experiment_instance_ids)
        fails = failing_experiment_instance_ids[self.experiment_instance_id]
        self.assertTrue(message in fails)
       
class LaboratoryServerSendingTestCase(unittest.TestCase):
    
    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        self.fake_client  = FakeClient()
        self.fake_locator = FakeLocator((self.fake_client,))
        locator = EasyLocator.EasyLocator(
                    CoordAddress.CoordAddress('mach','inst','serv'),
                    self.fake_locator
                  )

        self.experiment_instance_id = ExperimentInstanceId.ExperimentInstanceId("exp_inst","exp_name","exp_cat")
        self.experiment_coord_address = CoordAddress.CoordAddress.translate_address('myserver:myinstance@mymachine')

        cfg_manager._set_value('laboratory_assigned_experiments',
                        { 'exp_inst:exp_name@exp_cat': { 'coord_address': 'myserver1:myinstance@mymachine',
                                                         'checkers': ( ('WebcamIsUpAndRunningHandler', ("https://...",)),
                                                                       ('HostIsUpAndRunningHandler', ("hostname", 80), {}), )} })

        self.lab = LaboratoryServer.LaboratoryServer(
                None,
                locator,
                cfg_manager
            )


    def test_send_async_command_ok(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        commands_sent = [ "foo", "bar" ]
        
        responses = ["result1", "result2" ]
        request_ids = []
        
        self.fake_client.responses = responses[:]

        # We will send the commands asynchronously.
        for command in commands_sent:
            reqid = self.lab.do_send_async_command(lab_session_id, Command.Command(command))
            request_ids.append(reqid)
            
        # Build a dictionary relating the ids to the expected responses
        expected = dict(zip(request_ids, responses))
        
        is_first_time = True
        
        # We don't know how much time it will take so we have to keep checking
        # until we are done, for a maximum of 3 seconds.
        time_start = time.time()
        while(len(expected) > 0):
            
            result = self.lab.do_check_async_command_status(lab_session_id, request_ids)
            if is_first_time:
                self.assertEquals(2, len(result))
                is_first_time = False
            
            time_now = time.time()
            if(time_now - time_start > 3000):
                self.assertTrue(False, "Timeout while trying to run async commands")
                
            # Check every remaining command
            for id in expected.keys():
                tup = result[id]
                self.assertTrue( tup[0] in ("running", "ok", "error") )
                if(tup[0] == "ok"):
                    self.assertTrue(tup[1] in responses)
                    del expected[id]
                elif(tup[0] == "error"):
                    self.assertTrue(False, "Async command reported an error: " + tup[1] )
                    del expected[id]

        self.assertTrue( self.fake_client.verify_commands(commands_sent) )

    def test_send_command_ok(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        commands_sent = [ "foo", "bar" ]
        responses = ["result1", "result2" ]
        self.fake_client.responses = responses[:]

        for command in commands_sent:
            result = self.lab.do_send_command(lab_session_id, Command.Command(command))
            cur_response = responses.pop(0)
            self.assertEquals(cur_response, result.get_command_string())

        self.assertTrue( self.fake_client.verify_commands(commands_sent) )
 
    def test_send_command_fail(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        self.fake_client.fail = True

        self.assertRaises(
            LaboratoryExceptions.FailedToSendCommandException,
            self.lab.do_send_command,
            lab_session_id, 
            Command.Command("foo")
        )
        
    def test_send_async_command_fail(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        self.fake_client.fail = True
        
        reqid = self.lab.do_send_async_command(lab_session_id, Command.Command("foo"))
        
        # We don't know how much time it will take so we have to keep checking
        # until we are done, for a maximum of 3 seconds.
        time_start = time.time()
        while(True):
            time_now = time.time()
            if(time_now - time_start > 3000):
                self.assertTrue(False, "Timeout while trying to run async commands")
                
            result = self.lab.do_check_async_command_status(lab_session_id, (reqid,))
            tup = result[reqid]
                
            self.assertTrue( tup[0] in ("running", "ok", "error") )     
            self.assertNotEquals("ok", tup[0], "Expected an error")
            if(tup[0] != "running"):
                self.assertTrue("error", tup[0])
                self.assertTrue(tup[1] is not None)  
                break  
        return 

    def test_send_async_file_ok(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        files_sent = [ ("foo", "file_info1"), ("bar", "file_info2") ]
        
        responses = ["result1", "result2" ]
        request_ids = []
        
        self.fake_client.responses = responses[:]

        # We will send the commands asynchronously.
        for file in files_sent:
            reqid = self.lab.do_send_async_file(lab_session_id, file[0], file[1])
            request_ids.append(reqid)
            
        # Build a dictionary relating the ids to the expected responses
        expected = dict(zip(request_ids, responses))
        
        is_first_time = True
        
        # We don't know how much time it will take so we have to keep checking
        # until we are done, for a maximum of 3 seconds.
        time_start = time.time()
        while(len(expected) > 0):
            
            result = self.lab.do_check_async_command_status(lab_session_id, request_ids)
            if is_first_time:
                self.assertEquals(2, len(result))
                is_first_time = False
            
            time_now = time.time()
            if(time_now - time_start > 3000):
                self.assertTrue(False, "Timeout while trying to run async send_file")
                
            # Check every remaining command
            for id in expected.keys():
                tup = result[id]
                self.assertTrue( tup[0] in ("running", "ok", "error") )
                if(tup[0] == "ok"):
                    self.assertTrue(tup[1] in responses)
                    del expected[id]
                elif(tup[0] == "error"):
                    self.assertTrue(False, "Async send_file reported an error: " + tup[1] )
                    del expected[id]

        # TODO: Add this somehow, taking into account thread-safety.
        # self.assertTrue( self.fake_client.verify_files(files_sent) )

    def test_send_file_ok(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        files_sent = [ ("foo", "file_info1"), ("bar", "file_info2") ]
        responses = ["result1", "result2" ]
        self.fake_client.responses = responses[:]

        for (file_sent, file_info) in files_sent:
            result = self.lab.do_send_file(lab_session_id, file_sent, file_info)
            cur_response = responses.pop(0)
            self.assertEquals(cur_response, result.get_command_string())

        # TODO: Add this somehow, taking into account thread-safety.
        # self.assertTrue( self.fake_client.verify_files(files_sent) )
    
    def test_send_async_file_fail(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        self.fake_client.fail = True
        
        reqid = self.lab.do_send_async_file(lab_session_id, "foo", "file_info")
        
        # We don't know how much time it will take so we have to keep checking
        # until we are done, for a maximum of 3 seconds.
        time_start = time.time()
        while(True):
            time_now = time.time()
            if(time_now - time_start > 3000):
                self.assertTrue(False, "Timeout while trying to run async commands")
                
            result = self.lab.do_check_async_command_status(lab_session_id, (reqid,))
            tup = result[reqid]
                
            self.assertTrue( tup[0] in ("running", "ok", "error") )     
            self.assertNotEquals("ok", tup[0], "Expected an error")
            if(tup[0] != "running"):
                self.assertTrue("error", tup[0])
                self.assertTrue(tup[1] is not None)
                break  
        return 
    
    def test_send_file_fail(self):
        lab_session_id = self.lab.do_reserve_experiment(self.experiment_instance_id)
        self.fake_client.fail = True

        self.assertRaises(
            LaboratoryExceptions.FailedToSendFileException,
            self.lab.do_send_file,
            lab_session_id, 
            "foo",
            "file_info"
        )


###################################################################
# 
#   F A K E      O B J E C T S 
#  


###############################################
# Fake Locator
# 
class FakeLocator(object):
    def __init__(self, clients):
        self.clients = clients
        self.fail_on_server_request = None

    def retrieve_methods(self, server_type):
        return weblab_methods.Experiment

    def get_server_from_coord_address(self, coord_address, client_coord_address, server_type, restrictions):
        if self.fail_on_server_request is None:
            return self.clients
        raise Exception(self.fail_on_server_request)

    def inform_server_not_working(self, server_not_working, server_type, restrictions_of_server):
        pass

###############################################
# Fake Client
# 

class FakeClient(object):
    
    def __init__(self):
        super(FakeClient,self).__init__()
        self.files     = []
        self.commands  = []
        self.responses = []
        self.fail = False
        self.started  = 0
        self.disposed = 0

    def start_experiment(self):
        self.started += 1

    def dispose(self):
        self.disposed += 1

    def send_command_to_device(self, command):
        if self.fail:
            raise ProtocolExceptions.RemoteException("lelele","Lalala")
        else:
            self.commands.append(command)
            return self.responses.pop(0)

    def send_file_to_device(self, file, file_info):
        if self.fail:
            raise ProtocolExceptions.RemoteException("lelele","Lalala")
        else:
            self.files.append((file, file_info))
            return self.responses.pop(0)
    
    def verify_commands(self, expected):
        return self.commands == expected
    
    def verify_files(self, expected):
        return self.files == expected


###################################################################  

def suite():
    return unittest.TestSuite(
            (
                unittest.makeSuite(LaboratoryServerLoadingTestCase),
                unittest.makeSuite(LaboratoryServerManagementTestCase),
                unittest.makeSuite(LaboratoryServerSendingTestCase)
            )
        )

if __name__ == '__main__':
    unittest.main()

