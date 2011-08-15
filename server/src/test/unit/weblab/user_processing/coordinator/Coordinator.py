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
# 

import time
import datetime
import unittest
import time as time_mod

try:
    import json as json_mod
    json = json_mod
except ImportError:
    import simplejson as json_module
    json = json_module

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.sessions.SessionId as SessionId

import weblab.user_processing.coordinator.Coordinator as Coordinator
from weblab.data.experiments.ExperimentId import ExperimentId
from weblab.data.experiments.ExperimentInstanceId import ExperimentInstanceId
from weblab.user_processing.coordinator.Resource import Resource

import weblab.user_processing.coordinator.WebLabSchedulingStatus as WSS
import weblab.exceptions.user_processing.CoordinatorExceptions as CoordExc

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

DEFAULT_PRIORITY = 5
DEFAULT_TIME = 30
DEFAULT_INITIAL_DATA = 'this is the initial data that must be sent to the experiment'

class WrappedTimeProvider(Coordinator.TimeProvider):
    def get_time(self):
        if hasattr(self, '_TEST_TIME'):
            return self._TEST_TIME
        else:
            return super(WrappedTimeProvider, self).get_time()

class WrappedCoordinator(Coordinator.Coordinator):
    CoordinatorTimeProvider = WrappedTimeProvider

class ConfirmerMock(object):
    def __init__(self, coordinator, locator):
        self.uses_confirm = []
        self.uses_free    = []
        self.coordinator  = coordinator
    def enqueue_confirmation(self, lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data):
        self.uses_confirm.append((lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data))
    def enqueue_free_experiment(self, lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id):
        if lab_session_id is not None:
            self.uses_free.append((lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id))
        experiment_response = None
        initial_time = end_time = datetime.datetime.now()
        self.coordinator.confirm_resource_disposal(lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time)

SLOW_CONFIRMER_TIME = 0.05

class SlowConfirmerMock(object):
    def __init__(self, coordinator, locator):
        self.uses_confirm = []
        self.uses_free    = []
        self.coordinator  = coordinator
        self.times        = 3
    def enqueue_confirmation(self, lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data):
        self.uses_confirm.append((lab_coordaddress, reservation_id, experiment_instance_id, client_initial_data, server_initial_data))
        self.times        = 3
    def enqueue_free_experiment(self, lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id):
        self.times -= 1
        if self.times == 0:
            experiment_response = json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : True, Coordinator.FINISH_DATA_MESSAGE : "final response" })
        else:
            experiment_response = json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : False, Coordinator.FINISH_ASK_AGAIN_MESSAGE : SLOW_CONFIRMER_TIME })

        if lab_session_id is not None:
            self.uses_free.append((lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id))

        initial_time = end_time = datetime.datetime.now()
        self.coordinator.confirm_resource_disposal(lab_coordaddress, reservation_id, lab_session_id, experiment_instance_id, experiment_response, initial_time, end_time)


def coord_addr(coord_addr_str):
    return CoordAddress.CoordAddress.translate_address( coord_addr_str )

class CoordinatorTestCase(unittest.TestCase):
    def setUp(self):
        locator_mock = None

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = WrappedCoordinator(locator_mock, self.cfg_manager, ConfirmerClass = ConfirmerMock)
        self.coordinator._clean()

        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('inst1', 'exp1','cat1'), Resource("res_type", "res_inst1"))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('inst2', 'exp1','cat1'), Resource("res_type", "res_inst2"))

    def test_reserve_experiment(self):

        "Reserve an experiment "

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

    def test_list_experiments(self):

        "List the available experiments"

        experiment_ids = self.coordinator.list_experiments()
        self.assertEquals( 1, len(experiment_ids ) )
        self.assertEquals( ExperimentId('exp1', 'cat1'), experiment_ids[0] )

    def test_list_laboratories_addresses(self):

        "List the available laboratories"

        addresses = self.coordinator.list_laboratories_addresses()
        self.assertEquals( 2, len(addresses ) )
        self.assertTrue( "lab1:inst@machine" in addresses )
        self.assertTrue( "lab2:inst@machine" in addresses )


    def test_list_resource_types(self):

        "List the available resource types"

        resource_types = self.coordinator.list_resource_types()
        self.assertTrue( "res_type" in resource_types )


    def test_list_sessions_not_found(self):

        "List the available sessions for an experiment which does not exist "

        self.assertRaises( CoordExc.ExperimentNotFoundException,
            self.coordinator.list_sessions, ExperimentId('not','found') )

    def test_list_sessions_found(self):

        "List the available sessions for an experiment that exists, including current and waiting reservations"

        _, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        _, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        _, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
       
        result = self.coordinator.list_sessions( ExperimentId('exp1','cat1') )
        self.assertEquals( { 
                reservation1_id : WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME),
                reservation2_id : WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME),
                reservation3_id : WSS.WaitingQueueStatus(0)
            }, result )



    def test_reserve_not_existing_experiment(self):

        "Reserve an experiment that doesn't exist"

        self.assertRaises(
            CoordExc.ExperimentNotFoundException,
            self.coordinator.reserve_experiment,
            ExperimentId("this.doesnt.exist","this.neither"), 
            DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA )


    def test_add_redundant_experiment(self):

        """Adding redundant experiments is not a problem, but adding the experiment 
        with a different configuration is a problem"""

        # 
        # Adding twice an experiment that already exists is not a problem
        # 
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('inst2', 'exp1', 'cat1'), Resource("res_type", "res_inst2"))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('inst2', 'exp1', 'cat1'), Resource("res_type", "res_inst2"))

        # 
        # But saying that that experiment is handled by other lab server 
        # is actually a problem
        # 
        self.assertRaises(
                CoordExc.InvalidExperimentConfigException,
                self.coordinator.add_experiment_instance_id,
                "lab3:inst@machine",  # This is different
                ExperimentInstanceId('inst2', 'exp1', 'cat1'),
                Resource("res_type", "res_inst2")
            )

        # 
        # Or saying that that experiment is bound to other resource instance
        # 
        self.assertRaises(
                CoordExc.InvalidExperimentConfigException,
                self.coordinator.add_experiment_instance_id,
                "lab2:inst@machine",  
                ExperimentInstanceId('inst2', 'exp1', 'cat1'),
                Resource("res_type", "res_inst3") # Now this is different
            )


    def test_reserve_experiment_with_priority(self):

        "Reserve an experiment with different priorities to check that a more priority user moves faster in the queue "

        # 
        # Two normal users come in and get their experiments
        # 
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        # 
        # Now, one user with a priority of 4 and then another comes with a priority of 3. We check that the second user 
        # gets the first position
        # 
        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, 4, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0) # In the very first moment
        self.assertEquals( expected_status, status )

        status, reservation4_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, 3, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0) # Now he's the first
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation3_id)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        # 
        # Check that if a fifth user comes with priority 3, he will be after the number 4, 
        # but still before number 3
        # 
        status, reservation5_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, 3, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(1) 
        self.assertEquals( expected_status, status )
      
        
    def test_adding_experiment_instance_updates_waiting_users(self):

        "If there are users waiting in the queue, and a new instance is added, then the queue is updated "

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )
       
        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )
       
        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )
       
        status, reservation4_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        self.coordinator.add_experiment_instance_id("lab3:inst@machine", ExperimentInstanceId('inst3', 'exp1','cat1'), Resource("res_type", "res_inst4"))

        status = self.coordinator.get_reservation_status(reservation3_id)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab3:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation4_id)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

    def test_adding_experiment_instance_updates_waiting_instances_users(self):

        " If there are users waiting for instances, and a new instance is added, then the queue is updated "

        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst1", "exp1","cat1"))
        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst2", "exp1","cat1"))

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingInstancesQueueStatus(0)
        self.assertEquals( expected_status, status )
       
        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingInstancesQueueStatus(1)
        self.assertEquals( expected_status, status )
       
        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('inst1', 'exp1','cat1'), Resource("res_type", "res_inst1"))

        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation2_id)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )



    def test_timeout_by_not_using_experiment(self):

        "If a user doesn't poll enough, he's removed from the queue "

        now = time_mod.time()
        self.coordinator.time_provider._TEST_TIME = now

        #
        # Three users reserve experiments. The first 2 will be in WaitingConfirmation
        # 
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status1 = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status1, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status2 = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status2, status )

        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status3 = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status3, status )

        # 
        # Check again, the status is the same.
        # 
        status = self.coordinator.get_reservation_status(reservation1_id)
        self.assertEquals( expected_status1, status )

        status = self.coordinator.get_reservation_status(reservation2_id)
        self.assertEquals( expected_status2, status )

        status = self.coordinator.get_reservation_status(reservation3_id)
        self.assertEquals( expected_status3, status )


        # 
        # Now, some time later (1 day after), they are all expired (both Current and Waiting Users)
        # 
        self.coordinator.time_provider._TEST_TIME = now + 3600 * 24
        self.assertRaises( CoordExc.ExpiredSessionException, self.coordinator.get_reservation_status, reservation1_id )
        self.assertRaises( CoordExc.ExpiredSessionException, self.coordinator.get_reservation_status, reservation2_id )
        self.assertRaises( CoordExc.ExpiredSessionException, self.coordinator.get_reservation_status, reservation3_id )

    def test_reserved_timed_out(self):

        "If a user has a position in the queue, and the time assigned finishes, then this user is removed"

        now = time_mod.time()
        self.coordinator.time_provider._TEST_TIME = now

        #
        # Three users reserve experiments. The first 2 will be in WaitingConfirmation
        # 
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status1 = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status1, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME * 2, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status2 = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME * 2)
        self.assertEquals( expected_status2, status )

        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status3 = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status3, status )

        # 
        # Check again, the status is the same.
        # 
        status = self.coordinator.get_reservation_status(reservation1_id)
        self.assertEquals( expected_status1, status )

        status = self.coordinator.get_reservation_status(reservation2_id)
        self.assertEquals( expected_status2, status )

        status = self.coordinator.get_reservation_status(reservation3_id)
        self.assertEquals( expected_status3, status )


        # 
        # Some time later (after "time" but before "time" * 2), the first student expired, the second didn't
        # and the third one is in WaitingConfirmation (actually, in expected_status1)
        # 
        self.coordinator.time_provider._TEST_TIME = now + DEFAULT_TIME * 1.5
        self.assertRaises( CoordExc.ExpiredSessionException, self.coordinator.get_reservation_status, reservation1_id )
        status = self.coordinator.get_reservation_status(reservation2_id)
        self.assertEquals( expected_status2, status )

        status = self.coordinator.get_reservation_status(reservation3_id)
        self.assertEquals( expected_status1, status )


    def test_reserve_experiment_reserved(self):

        "Reserve and confirm the reservation"

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        now = datetime.datetime.fromtimestamp(int(time.time()))
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        self.assertEquals( 1, len(self.coordinator.confirmer.uses_confirm) )
        self.assertEquals( u'lab1:inst@machine', self.coordinator.confirmer.uses_confirm[0][0] )
        self.assertEquals( ExperimentInstanceId('inst1','exp1','cat1'), self.coordinator.confirmer.uses_confirm[0][2] )

        self.coordinator.confirm_experiment(ExperimentInstanceId('inst1', 'exp1', 'cat1'), reservation1_id, SessionId.SessionId("mysessionid"), "{}", now, now)
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status = WSS.ReservedStatus(coord_addr("lab1:inst@machine"), SessionId.SessionId("mysessionid"), DEFAULT_TIME, "{}", now, now)
        try:
            self.assertEquals( expected_status, status )
        except AssertionError:
            expected_status = WSS.ReservedStatus(coord_addr("lab1:inst@machine"), SessionId.SessionId("mysessionid"), DEFAULT_TIME, "{}", now - datetime.timedelta(seconds=1), now)
            self.assertEquals( expected_status, status )

    def test_reserve_experiment_batch_reserved(self):

        "Reserve and confirm a batch reservation"

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        now = datetime.datetime.fromtimestamp(int(time.time()))
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        self.assertEquals( 1, len(self.coordinator.confirmer.uses_confirm) )
        self.assertEquals( u'lab1:inst@machine', self.coordinator.confirmer.uses_confirm[0][0] )
        self.assertEquals( ExperimentInstanceId('inst1','exp1','cat1'), self.coordinator.confirmer.uses_confirm[0][2] )

        self.coordinator.confirm_experiment(ExperimentInstanceId('inst1', 'exp1', 'cat1'), reservation1_id, SessionId.SessionId("mysessionid"), '{ "batch" : true, "initial_configuration" : { "foo" : "bar" } }', now, now)

        self.assertRaises( CoordExc.ExpiredSessionException, 
                            self.coordinator.get_reservation_status, reservation1_id)

        reservation_id, initial_configuration, initial_time, end_time = self.coordinator.initial_store.get()
        self.assertFalse(reservation_id is None)
        self.assertEquals({ "foo" : "bar" }, initial_configuration)
        self.assertEquals(now, initial_time)
        self.assertEquals(now, end_time)

    def test_reserve_experiment_rejected(self):

        "Reserve and reject the reservation. Check that the user will be the first one in the queue"

        #
        # First add four users. Two will be in WaitingConfirmation and two in the queue.
        #
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

        status, reservation4_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        # 
        # Remove the first instance of the experiment
        # 
        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst1", "exp1","cat1"))

        # 
        # Check that the first user is the first in the queue
        # 
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation3_id)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation4_id)
        expected_status = WSS.WaitingQueueStatus(2)
        self.assertEquals( expected_status, status )

        # Fix the broken experiment instance, check that the queue is restored

        self.coordinator.mark_resource_as_fixed(Resource("res_type","res_inst1"))

        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation3_id)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

        status = self.coordinator.get_reservation_status(reservation4_id)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )


    def test_reserve_experiment_waiting(self):

        "Reserve all the experiments to check that the next ones are in Waiting state"

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

        status, reservation4_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )



    def test_reserve_experiment_waiting_instances(self):

        "Removes all the instances and then reserve"

        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst1", "exp1","cat1"))
        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst2", "exp1","cat1"))


        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingInstancesQueueStatus(0)
        self.assertEquals( expected_status, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingInstancesQueueStatus(1)
        self.assertEquals( expected_status, status )



    def test_get_reservation_status_expired_session(self):

        "If a user has no reservation, an ExpiredSessionException is raised"

        self.assertRaises( CoordExc.ExpiredSessionException, self.coordinator.get_reservation_status, 1 )

    def test_remove_experiment_id(self):

        "There is no problem removing experiment instances"

        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst1", "exp1","cat1"))
        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst2", "exp1","cat1"))

    def test_finish_user(self):

        "If we finish a user, he doesn't exist anymore"

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        self.coordinator.finish_reservation(reservation1_id)

        self.assertRaises( CoordExc.ExpiredSessionException, self.coordinator.get_reservation_status, reservation1_id )


    def test_remove_current_user_frees_queue(self):

        "If a user finishes and had some room, this room is reused"

        self.coordinator.mark_experiment_as_broken(ExperimentInstanceId("inst2", "exp1","cat1"))

        # Now there is a single experiment instance available. We reserve it:

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

        # Then we put other user in the queue:

        next_waiting_status = WSS.WaitingQueueStatus(0)

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = next_waiting_status
        self.assertEquals( expected_status, status )
        # And we finish the first reservation

        self.coordinator.finish_reservation(reservation1_id)
        # The second reservation should soon be in WaitingConfirmation status

        status = self.coordinator.get_reservation_status(reservation2_id)
        timeout = 1.0
        wait_time = 0.01
        counter = timeout / wait_time
        while status == next_waiting_status and counter >= 0:
            time_mod.sleep(wait_time)
            status = self.coordinator.get_reservation_status(reservation2_id)
            counter -= 1
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )

class CoordinatorMultiResourceTestCase(unittest.TestCase):
    def setUp(self):
        locator_mock = None

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = WrappedCoordinator(locator_mock, self.cfg_manager, ConfirmerClass = ConfirmerMock)
        self.coordinator._clean()

    def _deploy_cplds_and_fpgas_configuration(self):
        # 
        # There are 3 physical devices:
        # - pld1  (pld boards), in lab1:inst@machine
        # - pld2  (pld boards), in lab2:inst@machine
        # - fpga1 (fpga boards), in lab3:inst@machine
        # 
        # There are 3 types of experiments:
        # - ud-pld@PLD experiments, which can only run on pld boards
        # - ud-fpga@FPGA experiments, which can only run on fpga boards
        # - ud-binary@Binary experiments, which can run on both types of boards
        # 
        # And we are managing 5 experiment instances:
        # - exp1:binary@Binary experiments (using pld1:pld boards)
        # - exp2:binary@Binary experiments (using fpga1:fpga boards)
        # - exp1:ud-pld@PLD experiments (using pld1:pld boards)
        # - exp2:ud-pld@PLD experiments (using pld2@pld boards)
        # - exp1:ud-fpga@FPGA experiments (using fpga1:fpga boards)
        #

        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('exp1', 'ud-binary','Binary experiments'), Resource("pld boards",  "pld1"  ))
        self.coordinator.add_experiment_instance_id("lab3:inst@machine", ExperimentInstanceId('exp2', 'ud-binary','Binary experiments'), Resource("fpga boards", "fpga1" ))
        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('exp1', 'ud-pld',   'PLD experiments'),    Resource("pld boards",  "pld1"  ))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('exp2', 'ud-pld',   'PLD experiments'),    Resource("pld boards",  "pld2"  ))
        self.coordinator.add_experiment_instance_id("lab3:inst@machine", ExperimentInstanceId('exp1', 'ud-fpga',  'FPGA experiments'),   Resource("fpga boards", "fpga1" ))

    def _deploy_cplds_only_configuration(self):
        # 
        # There are 2 physical devices:
        # - pld1  (pld boards), in lab1:inst@machine
        # - pld2  (pld boards), in lab2:inst@machine
        # 
        # There are 2 types of experiments:
        # - ud-pld@PLD experiments, which can only run on pld boards
        # - ud-binary@Binary experiments, which can run on both types of boards
        # 
        # And we are managing 3 experiment instances:
        # - exp1:binary@Binary experiments (using pld1:pld boards)
        # - exp1:ud-pld@PLD experiments (using pld1:pld boards)
        # - exp2:ud-pld@PLD experiments (using pld2@pld boards)
        #

        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('exp1', 'ud-binary','Binary experiments'), Resource("pld boards",  "pld1"  ))
        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('exp1', 'ud-pld',   'PLD experiments'),    Resource("pld boards",  "pld1"  ))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('exp2', 'ud-pld',   'PLD experiments'),    Resource("pld boards",  "pld2"  ))

    def test_reserve_resource_does_not_support_expected_experiment(self):
        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('exp1', 'ud-binary','Binary experiments'), Resource("pld boards",  "pld1"  ))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('exp2', 'ud-pld',   'PLD experiments'),    Resource("pld boards",  "pld2"  ))

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 1, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME + 1)
        self.assertEquals( expected_status, status )

    def test_reserve_resource_does_not_support_expected_experiment_and_there_are_waiting(self):
        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('exp1', 'ud-binary','Binary experiments'), Resource("pld boards",  "pld1"  ))
        self.coordinator.add_experiment_instance_id("lab2:inst@machine", ExperimentInstanceId('exp2', 'ud-pld',   'PLD experiments'),    Resource("pld boards",  "pld2"  ))

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 1, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME + 1)
        self.assertEquals( expected_status, status )

        # There is one student in the queue waiting for a "pld boards" that matches ud-pld
        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 2, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

        # There is a new student in the queue waiting for "pld boards" that matches ud-binary, but since it's free, it must be free
        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("ud-binary","Binary experiments"), DEFAULT_TIME + 3, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME + 3)
        self.assertEquals( expected_status, status )

    def test_reserve_full_scenario(self):
        self._deploy_cplds_and_fpgas_configuration()

        now = datetime.datetime.now()

        #
        # Two users requesting a CPLD and a user requesting a FPGA get what they want
        #

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 1, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME + 1)
        self.assertEquals( expected_status, status )

        status, reservation2_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 2, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME + 2)
        self.assertEquals( expected_status, status )

        status, reservation3_id = self.coordinator.reserve_experiment(ExperimentId("ud-fpga","FPGA experiments"), DEFAULT_TIME + 3, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab3:inst@machine"), DEFAULT_TIME + 3)
        self.assertEquals( expected_status, status )

        # 
        # Then, somebody comes and requests a Binary experiment. He is in queue, position 0, waiting for both pld1 and fpga1
        # 

        status, reservation4_id = self.coordinator.reserve_experiment(ExperimentId("ud-binary","Binary experiments"), DEFAULT_TIME + 4, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(0)
        self.assertEquals( expected_status, status )

        # 
        # Users requesting a FPGA or a CPLD will be in the next position
        # 

        status, reservation5_id = self.coordinator.reserve_experiment(ExperimentId("ud-fpga","FPGA experiments"), DEFAULT_TIME + 5, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        status, reservation6_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 6, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        # 
        # If another user comes requesting a CPLD, he will be in the second position
        # 
        status, reservation7_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 7, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(2)
        self.assertEquals( expected_status, status )

        # 
        # If a user comes requesting a Binary, he will be in position 2 rather than 3, since in the FPGA queues there are only two users before him
        # 
        status, reservation8_id = self.coordinator.reserve_experiment(ExperimentId("ud-binary","Binary experiments"), DEFAULT_TIME + 8, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(2)
        self.assertEquals( expected_status, status )

        # 
        # However, it's not that this reservation is only waiting for an FPGA. If the two guys waiting for a CPLD get out, this guy will be promoted
        # 
        self.coordinator.finish_reservation(reservation6_id)
        self.coordinator.finish_reservation(reservation7_id)

        status = self.coordinator.get_reservation_status(reservation8_id)
        expected_status = WSS.WaitingQueueStatus(1)
        self.assertEquals( expected_status, status )

        # 
        # If a new user requests a CPLD, then he'll be 3rd (position = 2), since he has both users requesting a ud-binary before him:
        # 
        status, reservation9_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 9, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingQueueStatus(2)
        self.assertEquals( expected_status, status )

        # 
        # However, if the instance of the resource of "pld boards" that doesn't support ud-pld@PLD experiments is released, this last user goes first, since
        # the other people waiting for "pld boards" are waiting for a resource instance of "pld boards" that supports "ud-binary@Binary experiments"
        # 
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation2_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation2_id)

        status = self.coordinator.get_reservation_status(reservation9_id)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME + 9)
        self.assertEquals( expected_status, status )
     
        # 
        # If this user goes out, then that experiment is available, so next user requesting a ud-pld@PLD experiments will get it
        # 
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation9_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation9_id)

        status, reservation10_id = self.coordinator.reserve_experiment(ExperimentId("ud-pld","PLD experiments"), DEFAULT_TIME + 10, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab2:inst@machine"), DEFAULT_TIME + 10)
        self.assertEquals( expected_status, status )

        # 
        # If the user who was using the FPGA leaves it, the first user waiting for a
        # binary experiment will get it.
        # 
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation3_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation3_id)

        status = self.coordinator.get_reservation_status(reservation4_id)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab3:inst@machine"), DEFAULT_TIME + 4)
        self.assertEquals( expected_status, status )

        # If the user who was using the CPLD that supports binary leaves, the second user
        # waiting for a binary experiment will get it
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation1_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation1_id)

        status = self.coordinator.get_reservation_status(reservation8_id)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME + 8)
        self.assertEquals( expected_status, status )

        # 
        # We remove the rest of the queues
        # 
        self.coordinator.finish_reservation(reservation5_id)

        # And then the ones using the devices
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation4_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation4_id)
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation8_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation8_id)
        self.coordinator.confirm_experiment(ExperimentInstanceId('???','ud-pld','PLD experiments'), reservation10_id, SessionId.SessionId("the.session"), "{}", now, now)
        self.coordinator.finish_reservation(reservation10_id)



class CoordinatorWithSlowConfirmerTestCase(unittest.TestCase):
    def setUp(self):
        locator_mock = None

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = WrappedCoordinator(locator_mock, self.cfg_manager, ConfirmerClass = SlowConfirmerMock)
        self.coordinator._clean()

        self.coordinator.add_experiment_instance_id("lab1:inst@machine", ExperimentInstanceId('inst1', 'exp1','cat1'), Resource("res_type", "res_inst1"))

    def test_confirming_free_experiment(self):
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId("exp1","cat1"), DEFAULT_TIME, DEFAULT_PRIORITY, DEFAULT_INITIAL_DATA)
        expected_status = WSS.WaitingConfirmationQueueStatus(coord_addr("lab1:inst@machine"), DEFAULT_TIME)
        self.assertEquals( expected_status, status )
        previous = time_mod.time()
        self.coordinator.finish_reservation(reservation1_id)
        next = time_mod.time()
        self.assertTrue( next - previous > SLOW_CONFIRMER_TIME * 2)
        self.assertEquals( 0, self.coordinator.confirmer.times)

def suite():
    return unittest.TestSuite( (
                    unittest.makeSuite(CoordinatorTestCase),
                    unittest.makeSuite(CoordinatorMultiResourceTestCase),
                ) )

if __name__ == '__main__':
    unittest.main()


