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

import unittest
import datetime
import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

from test.unit.weblab.core.coordinator.coordinator import WrappedSqlCoordinator, WrappedRedisCoordinator, ConfirmerMock

class AbstractPostReservationDataManagerTestCase(unittest.TestCase):
    def setUp(self):

        locator_mock = None

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = self.WrappedCoordinator(locator_mock, self.cfg_manager, ConfirmerClass = ConfirmerMock)
        self.coordinator._clean()

        self.post_reservation_data_manager = self.coordinator.post_reservation_data_manager
        self.time_provider = self.coordinator.time_provider

    def tearDown(self):
        self.coordinator.stop()

    def test_create_find(self):
        reservation_id = "my-id"
        now = self.time_provider.get_datetime()
        initial_data = '{ "initial" : "data" }'
        end_data     = '{ "end"     : "data" }'
        expiration = now + datetime.timedelta(seconds=1000)
        self.post_reservation_data_manager.create(reservation_id, now, expiration, initial_data)

        status = self.post_reservation_data_manager.find(reservation_id)

        self.assertEquals(initial_data, status.initial_data)
        self.assertFalse(status.finished)
        self.assertEquals(None, status.end_data)

        self.post_reservation_data_manager.finish(reservation_id, end_data)

        status = self.post_reservation_data_manager.find(reservation_id)

        self.assertEquals(initial_data, status.initial_data)
        self.assertTrue(status.finished)
        self.assertEquals(end_data, status.end_data)

    def test_expired(self):
        reservation_id = "my-id"
        now = self.time_provider.get_datetime()
        initial_data = '{ "initial" : "data" }'
        expiration = now - datetime.timedelta(seconds=1)

        self.post_reservation_data_manager.create(reservation_id, now, expiration, initial_data)

        self.post_reservation_data_manager.clean_expired()

        status = self.post_reservation_data_manager.find(reservation_id)
        self.assertEquals(None, status)

        expiration = now + datetime.timedelta(seconds=1000)

        self.post_reservation_data_manager.create(reservation_id, now, expiration, initial_data)
        self.post_reservation_data_manager.clean_expired()

        status = self.post_reservation_data_manager.find(reservation_id)
        self.assertNotEqual(None, status)


class SqlPostReservationDataManagerTestCase(AbstractPostReservationDataManagerTestCase):
    WrappedCoordinator = WrappedSqlCoordinator

class RedisPostReservationDataManagerTestCase(AbstractPostReservationDataManagerTestCase):
    WrappedCoordinator = WrappedRedisCoordinator

def suite():
    return unittest.TestSuite((
                unittest.makeSuite(SqlPostReservationDataManagerTestCase),
                unittest.makeSuite(RedisPostReservationDataManagerTestCase),
            ))


if __name__ == '__main__':
    unittest.main()

