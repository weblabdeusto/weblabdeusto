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
from voodoo.override import Override

import weblab.user_processing.TemporalInformationRetriever as TemporalInformationRetriever
import weblab.user_processing.coordinator.TemporalInformationStore as TemporalInformationStore

RESERVATION1 = 'reservation_id1'
RESERVATION2 = 'reservation_id2'
RESERVATION3 = 'reservation_id3'

DATA1 = {'data' : 1 }
DATA2 = {'data' : 2 }
DATA3 = {'data' : 3 }

class TemporalInformationRetrieverTestCase(unittest.TestCase):
    def setUp(self):

        self.batch_store    = TemporalInformationStore.TemporalInformationStore()
        self.finished_store = TemporalInformationStore.TemporalInformationStore()

        self.retriever = TemporalInformationRetriever.TemporalInformationRetriever(self.batch_store, self.finished_store)
        self.retriever.timeout = 0.01 # Be quicker instead of waiting for half a second

    def test_retriever(self):
        self.retriever.start()
        try:
            self.batch_store.put(RESERVATION1, DATA1)
            self.batch_store.put(RESERVATION2, DATA2)
            self.batch_store.put(RESERVATION3, DATA3)
            pass
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
        batch_store    = TemporalInformationStore.TemporalInformationStore()
        finished_store = TemporalInformationStore.TemporalInformationStore()
        fake = FakeTemporalInformationRetriever(batch_store, finished_store)
        fake.start()
        try:
            time.sleep(0.01)
            self.assertTrue( hasattr( fake, 'failures' ) )
            self.assertTrue( fake.failures > 1 )
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

