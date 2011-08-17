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


import unittest
import time
import datetime
from voodoo.override import Override

import weblab.user_processing.TemporalInformationRetriever as TemporalInformationRetriever
import weblab.user_processing.coordinator.TemporalInformationStore as TemporalInformationStore

import weblab.user_processing.database.DatabaseGateway as DatabaseGateway
import test.unit.configuration as configuration
from test.unit.weblab.user_processing.database.DatabaseMySQLGateway import create_usage

import voodoo.configuration.ConfigurationManager as ConfigurationManager

RESERVATION1 = 'reservation_id1'
RESERVATION2 = 'reservation_id2'
RESERVATION3 = 'reservation_id3'
RESERVATION4 = 'reservation_id4'

DATA1 = "{'data' : 1 }"
DATA2 = "{'data' : 2 }"
DATA3 = "{'data' : 3 }"
DATA4 = "{'data' : 4 }"

def wait_for(retriever, iterations = 5, max_wait = 10):
    initial_time = time.time()
    initial_iterations = retriever.iterations
    while retriever.iterations - initial_iterations < iterations:
        time.sleep(0.01)
        if time.time() - initial_time >= max_wait:
            raise AssertionError("Maximum time waiting reached")

class TemporalInformationRetrieverTestCase(unittest.TestCase):
    def setUp(self):

        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.gateway = DatabaseGateway.create_gateway(cfg_manager)
        self.gateway._delete_all_uses()

        self.initial_store    = TemporalInformationStore.InitialTemporalInformationStore()
        self.finished_store = TemporalInformationStore.FinishTemporalInformationStore()

        self.retriever = TemporalInformationRetriever.TemporalInformationRetriever(self.initial_store, self.finished_store, self.gateway)
        self.retriever.timeout = 0.001 # Be quicker instead of waiting for half a second
        
    def test_retriever_before(self):
        initial_time = end_time = datetime.datetime.now()
        self.retriever.start()
        try:
            # Make the system store the information
            self.initial_store.put(RESERVATION1, DATA1, initial_time, end_time)
            self.initial_store.put(RESERVATION2, DATA2, initial_time, end_time)
            self.initial_store.put(RESERVATION3, DATA3, initial_time, end_time)
            self.finished_store.put(RESERVATION4, DATA4, initial_time, end_time)
            
            # Wait and then populate the RESERVATION3 (the last one in the queue)
            wait_for(self.retriever)
            
            usage_return_values = create_usage(self.gateway, RESERVATION3)
            student1 = usage_return_values[0]
            usages = self.gateway.list_usages_per_user(student1.login)
            self.assertEquals(1, len(usages))

            wait_for(self.retriever)

            # And check that it has been stored
            full_usage3 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals("@@@initial@@@", full_usage3.commands[-1].command.commandstring)
            self.assertEquals(DATA3, full_usage3.commands[-1].response.commandstring)

            # So the the same with the rest
            create_usage(self.gateway, RESERVATION1)
            create_usage(self.gateway, RESERVATION2)
            create_usage(self.gateway, RESERVATION4)

            usages = self.gateway.list_usages_per_user(student1.login)
            self.assertEquals(4, len(usages))

            # Wait and check that it has also been stored
            wait_for(self.retriever)

            full_usage1 = self.gateway.retrieve_usage(usages[1].experiment_use_id)
            self.assertEquals("@@@initial@@@", full_usage1.commands[-1].command.commandstring)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)

            full_usage2 = self.gateway.retrieve_usage(usages[2].experiment_use_id)
            self.assertEquals("@@@initial@@@", full_usage2.commands[-1].command.commandstring)
            self.assertEquals(DATA2, full_usage2.commands[-1].response.commandstring)

            full_usage4 = self.gateway.retrieve_usage(usages[3].experiment_use_id)
            self.assertEquals("@@@finish@@@", full_usage4.commands[-1].command.commandstring)
            self.assertEquals(DATA4, full_usage4.commands[-1].response.commandstring)

        finally:
            self.retriever.stop()
            self.retriever.join(1)
            self.assertFalse(self.retriever.isAlive())

    def test_retriever_after(self):
        initial_time = end_time = datetime.datetime.now()
        self.retriever.start()
        try:
            # Create the structure in the database
            usage_return_values = create_usage(self.gateway, RESERVATION1)
            create_usage(self.gateway, RESERVATION2)
            create_usage(self.gateway, RESERVATION3)
            student1 = usage_return_values[0]
            usages = self.gateway.list_usages_per_user(student1.login)
            self.assertEquals(3, len(usages))

            # Wait 
            wait_for(self.retriever)

            # Start populating the initial information

            self.initial_store.put(RESERVATION1, DATA1, initial_time, end_time)
            self.initial_store.put(RESERVATION2, DATA2, initial_time, end_time)
            self.initial_store.put(RESERVATION3, DATA3, initial_time, end_time)

            wait_for(self.retriever)

            full_usage1 = self.gateway.retrieve_usage(usages[0].experiment_use_id)
            self.assertEquals("@@@initial@@@", full_usage1.commands[-1].command.commandstring)
            self.assertEquals(DATA1, full_usage1.commands[-1].response.commandstring)

            full_usage2 = self.gateway.retrieve_usage(usages[1].experiment_use_id)
            self.assertEquals("@@@initial@@@", full_usage2.commands[-1].command.commandstring)
            self.assertEquals(DATA2, full_usage2.commands[-1].response.commandstring)

            full_usage3 = self.gateway.retrieve_usage(usages[2].experiment_use_id)
            self.assertEquals("@@@initial@@@", full_usage3.commands[-1].command.commandstring)
            self.assertEquals(DATA3, full_usage3.commands[-1].response.commandstring)
        finally:
            self.retriever.stop()
            self.retriever.join(1)
            self.assertFalse(self.retriever.isAlive())

class FakeTemporalInformationRetriever(TemporalInformationRetriever.TemporalInformationRetriever):

    @Override(TemporalInformationRetriever.TemporalInformationRetriever)
    def iterate(self):
        failures = getattr(self, 'failures', 0)
        self.failures = failures + 1
        return 10 / 0 # cause an error


class IterationFailerTemporalInformationRetrieverTestCase(unittest.TestCase):
    def test_fail(self):
        initial_store    = TemporalInformationStore.InitialTemporalInformationStore()
        finished_store = TemporalInformationStore.FinishTemporalInformationStore()
        fake = FakeTemporalInformationRetriever(initial_store, finished_store, None)
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

