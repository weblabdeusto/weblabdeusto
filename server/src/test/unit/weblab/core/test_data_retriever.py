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
#
from __future__ import print_function, unicode_literals


import unittest
import time
import datetime
from voodoo.override import Override

from voodoo.gen import CoordAddress

from weblab.data.experiments import ExperimentId
from weblab.data.command import Command

import weblab.core.data_retriever as TemporalInformationRetriever
import weblab.core.coordinator.store as TemporalInformationStore

from weblab.core.db import DatabaseGateway
import test.unit.configuration as configuration

import voodoo.configuration as ConfigurationManager

RESERVATION1 = 'reservation_id1'
RESERVATION2 = 'reservation_id2'
RESERVATION3 = 'reservation_id3'
RESERVATION4 = 'reservation_id4'

DATA1 = "{'data' : 1 }"
DATA2 = "{'data' : 2 }"
DATA3 = "{'data' : 3 }"
DATA4 = "{'data' : 4 }"

DATA_REQUEST1 = "{'foo' : 1}"
DATA_REQUEST2 = "{'foo' : 1}"
DATA_REQUEST3 = "{'foo' : 1}"
DATA_REQUEST4 = "{'foo' : 1}"

def wait_for(retriever, iterations = 5, max_wait = 10):
    initial_time = time.time()
    initial_iterations = retriever.iterations
    while retriever.iterations - initial_iterations < iterations:
        time.sleep(0.01)
        if time.time() - initial_time >= max_wait:
            raise AssertionError("Maximum time waiting reached")

def coord_addr(coord_addr_str):
    return CoordAddress.translate( coord_addr_str )

class TemporalInformationRetrieverTestCase(unittest.TestCase):
    def setUp(self):

        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.dbmanager = DatabaseGateway(cfg_manager)
        self.dbmanager._delete_all_uses()
        session = self.dbmanager.Session()
        try:    
            student1 = self.dbmanager._get_user(session, 'student1')
        finally:
            session.close()

        self.initial_store  = TemporalInformationStore.InitialTemporalInformationStore()
        self.finished_store = TemporalInformationStore.FinishTemporalInformationStore()
        self.commands_store = TemporalInformationStore.CommandsTemporalInformationStore()
        self.completed_store = TemporalInformationStore.CompletedInformationStore()

        self.retriever = TemporalInformationRetriever.TemporalInformationRetriever(cfg_manager, self.initial_store, self.finished_store, self.commands_store, self.completed_store, self.dbmanager)
        self.retriever.timeout = 0.001 # Be quicker instead of waiting for half a second

        self.initial_time = self.end_time = datetime.datetime.now()
        self.initial_timestamp = self.end_timestamp = time.time()

        request_info = {'username':'student1','role':'student','permission_scope' : 'user', 'permission_id' : student1.id}
        exp_id = ExperimentId('ud-dummy','Dummy Experiments')

        self.entry1 = TemporalInformationStore.InitialInformationEntry(
                        RESERVATION1, exp_id, coord_addr('ser:inst@mach'),
                        DATA1, self.initial_time, self.end_time, request_info.copy(), DATA_REQUEST1)
        self.entry2 = TemporalInformationStore.InitialInformationEntry(
                        RESERVATION2, exp_id, coord_addr('ser:inst@mach'),
                        DATA2, self.initial_time, self.end_time, request_info.copy(), DATA_REQUEST2)
        self.entry3 = TemporalInformationStore.InitialInformationEntry(
                        RESERVATION3, exp_id, coord_addr('ser:inst@mach'),
                        DATA3, self.initial_time, self.end_time, request_info.copy(), DATA_REQUEST3)
        self.entry4 = TemporalInformationStore.InitialInformationEntry(
                        RESERVATION4, exp_id, coord_addr('ser:inst@mach'),
                        DATA4, self.initial_time, self.end_time, request_info.copy(), DATA_REQUEST3)


    def test_initial_finish(self):
        self.retriever.start()
        try:
            usages = self.dbmanager.list_usages_per_user('student1')
            self.assertEquals(0, len(usages))

            self.initial_store.put(self.entry1)
            self.initial_store.put(self.entry2)
            self.initial_store.put(self.entry3)
            self.finished_store.put(RESERVATION4, DATA4, self.initial_time, self.end_time)

            # Wait and then populate the RESERVATION3 (the last one in the queue)
            wait_for(self.retriever)

            usages = self.dbmanager.list_usages_per_user('student1')
            # There are 3, and RESERVATION4 is waiting
            self.assertEquals(3, len(usages))

            # Check that it has been stored
            full_usage1 = self.dbmanager.retrieve_usage(usages[0].experiment_use_id)

            self.assertEquals("@@@initial::request@@@", full_usage1.commands[-2].command.commandstring)
            self.assertEquals(DATA_REQUEST1, full_usage1.commands[-2].response.commandstring)
            self.assertEquals("@@@initial::response@@@", full_usage1.commands[-1].command.commandstring)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)
            self.assertEquals(None, full_usage1.end_date)

            full_usage2 = self.dbmanager.retrieve_usage(usages[1].experiment_use_id)
            self.assertEquals(DATA2, full_usage2.commands[-1].response.commandstring)
            self.assertEquals(None, full_usage2.end_date)
            full_usage3 = self.dbmanager.retrieve_usage(usages[2].experiment_use_id)
            self.assertEquals(DATA3, full_usage3.commands[-1].response.commandstring)
            self.assertEquals(None, full_usage3.end_date)

            wait_for(self.retriever)

            self.initial_store.put(self.entry4)

            wait_for(self.retriever)

            usages = self.dbmanager.list_usages_per_user('student1')
            # RESERVATION4 achieved
            self.assertEquals(4, len(usages))

            # And end_date is filled for 4
            full_usage4 = self.dbmanager.retrieve_usage(usages[3].experiment_use_id)
            self.assertEquals(DATA4, full_usage4.commands[-1].response.commandstring)
            self.assertNotEqual(None, full_usage4.end_date)

            # While in the rest it's not yet filled

            full_usage1 = self.dbmanager.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)
            self.assertEquals(None, full_usage1.end_date)

            full_usage2 = self.dbmanager.retrieve_usage(usages[1].experiment_use_id)
            self.assertEquals(DATA2, full_usage2.commands[-1].response.commandstring)
            self.assertEquals(None, full_usage2.end_date)

            full_usage3 = self.dbmanager.retrieve_usage(usages[2].experiment_use_id)
            self.assertEquals(DATA3, full_usage3.commands[-1].response.commandstring)
            self.assertEquals(None, full_usage3.end_date)

            # But if we add to the finish store, and we wait:
            self.finished_store.put(RESERVATION1, DATA1, self.initial_time, self.end_time)

            wait_for(self.retriever)

            # Then it is filled
            full_usage1 = self.dbmanager.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)
            self.assertNotEqual(None, full_usage1.end_date)


        finally:
            self.retriever.stop()
            self.retriever.join(1)
            self.assertFalse(self.retriever.isAlive())

    def test_commands(self):
        self.retriever.start()
        try:
            usages = self.dbmanager.list_usages_per_user('student1')
            self.assertEquals(0, len(usages))

            self.initial_store.put(self.entry1)

            wait_for(self.retriever)

            usages = self.dbmanager.list_usages_per_user('student1')

            self.assertEquals(1, len(usages))

            entry_id1 = 58131
            entry_id2 = 14214
            entry_id3 = 84123

            pre_command1 = TemporalInformationStore.CommandOrFileInformationEntry(RESERVATION1, True, True, entry_id1, Command(DATA_REQUEST1), self.initial_timestamp)
            post_command1 = TemporalInformationStore.CommandOrFileInformationEntry(RESERVATION1, False, True, entry_id1, Command(DATA1), self.initial_timestamp)

            pre_command2 = TemporalInformationStore.CommandOrFileInformationEntry(RESERVATION2, True, True, entry_id2, Command(DATA_REQUEST2), self.initial_timestamp)
            post_command2 = TemporalInformationStore.CommandOrFileInformationEntry(RESERVATION2, False, True, entry_id2, Command(DATA2), self.initial_timestamp)

            pre_command3 = TemporalInformationStore.CommandOrFileInformationEntry(RESERVATION3, True, True, entry_id3, Command(DATA_REQUEST3), self.initial_timestamp)
            post_command3 = TemporalInformationStore.CommandOrFileInformationEntry(RESERVATION3, False, True, entry_id3, Command(DATA3), self.initial_timestamp)

            # The reservation is stored, therefore this command will
            # also be stored
            self.commands_store.put(pre_command1)

            # This reservation has not been stored, therefore this command
            # will not be stored yet
            self.commands_store.put(pre_command2)

            # Neither this reservation or the pre_command3 have been stored,
            # therefore this command will not be stored
            self.commands_store.put(post_command3)

            wait_for(self.retriever)

            usages = self.dbmanager.list_usages_per_user('student1')
            self.assertEquals(1, len(usages))

            full_usage1 = self.dbmanager.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals(DATA_REQUEST1, full_usage1.commands[-1].command.commandstring)
            self.assertEquals(None, full_usage1.commands[-1].response.commandstring)


            # So we add the post_command1, to avoid the "None"
            self.commands_store.put(post_command1)
            # And the pre_command3, to see if it is correctly enqueued
            self.commands_store.put(pre_command3)
            # And the entry 2, to let pre_command2 enter
            self.initial_store.put(self.entry2)

            wait_for(self.retriever)

            usages = self.dbmanager.list_usages_per_user('student1')
            self.assertEquals(2, len(usages))

            full_usage1 = self.dbmanager.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals(DATA_REQUEST1, full_usage1.commands[-1].command.commandstring)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)

            full_usage2 = self.dbmanager.retrieve_usage(usages[1].experiment_use_id)
            self.assertEquals(DATA_REQUEST2, full_usage2.commands[-1].command.commandstring)
            self.assertEquals(None, full_usage2.commands[-1].response.commandstring)

            # So now we add the rest

            self.commands_store.put(post_command2)
            self.initial_store.put(self.entry3)

            wait_for(self.retriever)

            usages = self.dbmanager.list_usages_per_user('student1')
            self.assertEquals(3, len(usages))

            full_usage1 = self.dbmanager.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals(DATA_REQUEST1, full_usage1.commands[-1].command.commandstring)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)

            full_usage2 = self.dbmanager.retrieve_usage(usages[1].experiment_use_id)
            self.assertEquals(DATA_REQUEST2, full_usage2.commands[-1].command.commandstring)
            self.assertEquals(DATA2, full_usage2.commands[-1].response.commandstring)

            full_usage3 = self.dbmanager.retrieve_usage(usages[2].experiment_use_id)
            self.assertEquals(DATA_REQUEST3, full_usage3.commands[-1].command.commandstring)
            self.assertEquals(DATA3, full_usage3.commands[-1].response.commandstring)

        finally:
            self.retriever.stop()
            self.retriever.join(1)
            self.assertFalse(self.retriever.isAlive())


class FakeTemporalInformationRetriever(TemporalInformationRetriever.TemporalInformationRetriever):

    PRINT_ERRORS = False

    @Override(TemporalInformationRetriever.TemporalInformationRetriever)
    def iterate(self):
        failures = getattr(self, 'failures', 0)
        self.failures = failures + 1
        return 10 / 0 # cause an error


class IterationFailerTemporalInformationRetrieverTestCase(unittest.TestCase):
    def test_fail(self):
        initial_store    = TemporalInformationStore.InitialTemporalInformationStore()
        finished_store   = TemporalInformationStore.FinishTemporalInformationStore()
        commands_store   = TemporalInformationStore.CommandsTemporalInformationStore()
        completed_store  = TemporalInformationStore.CompletedInformationStore()

        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)

        fake = FakeTemporalInformationRetriever(cfg_manager, initial_store, finished_store, commands_store, completed_store, None)
        fake.start()
        try:
            initial_time = time.time()

            while not hasattr( fake, 'failures') or fake.failures < 1:
                time.sleep(0.01)
                if time.time() - initial_time > 5:
                    raise AssertionError("Too long time passed waiting for failures to increase")
        finally:
            fake.stop()
            fake.join(1)
        self.assertFalse( fake.isAlive() )


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(TemporalInformationRetrieverTestCase),
            unittest.makeSuite(IterationFailerTemporalInformationRetrieverTestCase),
        ))

if __name__ == '__main__':
    unittest.main()

