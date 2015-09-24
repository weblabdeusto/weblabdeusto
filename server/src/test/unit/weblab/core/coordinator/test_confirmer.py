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

import time
import datetime
import unittest
import mocker

from voodoo.gen import CoordAddress
import voodoo.sessions.session_id           as SessionId

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import weblab.data.server_type as ServerType
import weblab.methods as weblab_methods
from weblab.data.experiments import ExperimentInstanceId
from weblab.data.experiments import ExperimentId
from weblab.core.coordinator.resource import Resource
from weblab.core.coordinator.config_parser import COORDINATOR_LABORATORY_SERVERS

from weblab.core.coordinator.gateway import create as coordinator_create, SQLALCHEMY

import weblab.core.coordinator.status as WSS

def coord_addr(coord_addr_str):
    return CoordAddress.translate( coord_addr_str )

DEFAULT_REQUEST_INFO = {'facebook' : False, 'mobile' : False}

class ConfirmerTestCase(mocker.MockerTestCase):

    def setUp(self):

        self.coord_address = CoordAddress.translate( "server0:instance0@machine0")

        self.mock_locator  = self.mocker.mock()

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        self.cfg_manager._set_value(COORDINATOR_LABORATORY_SERVERS, {
            u'lab1:inst@machine' : {
                'inst1|exp1|cat1' : 'res_inst@res_type'
            },
        })

        self.coordinator = coordinator_create(SQLALCHEMY, self.mock_locator, self.cfg_manager)
        self.coordinator._clean()
        self.confirmer   = self.coordinator.confirmer

        self.lab_address = u"lab1:inst@machine"
        self.coordinator.add_experiment_instance_id(self.lab_address, ExperimentInstanceId('inst1', 'exp1','cat1'), Resource("res_type", "res_inst"))

    def tearDown(self):
        self.coordinator.stop()

    def test_free_experiment_success(self):
        mock_laboratory = self.mocker.mock()
        mock_laboratory.free_experiment('lab_session_id')

        self.mock_locator[coord_addr(self.lab_address)]
        self.mocker.result(mock_laboratory)

        self.mocker.replay()
        self.confirmer.enqueue_free_experiment(self.lab_address, '5', 'lab_session_id', ExperimentInstanceId('inst1','exp1','cat1'))
        self.confirmer._free_handler.join()

    def test_free_experiment_raises_exception(self):
        self.mock_locator[coord_addr(self.lab_address)]
        self.mocker.throw( Exception('foo') )

        self.mocker.replay()
        self.confirmer.enqueue_free_experiment(self.lab_address, '5', 'lab_session_id', ExperimentInstanceId('inst1','exp1','cat1'))
        self.confirmer._free_handler.join()

        self.assertEquals( None, self.confirmer._free_handler.raised_exc )

    def test_confirm_experiment(self):
        lab_session_id = SessionId.SessionId("samplesession_id")

        mock_laboratory = self.mocker.mock()
        mock_laboratory.reserve_experiment(ExperimentInstanceId('inst1','exp1','cat1'), '"sample initial data"', mocker.ANY)
        self.mocker.result((lab_session_id, None, { 'address' : 'server:inst@mach'}))

        self.mock_locator[coord_addr(self.lab_address)]
        self.mocker.result(mock_laboratory)
        self.mocker.count(min=1,max=None)

        self.mocker.replay()
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5, True, 'sample initial data', DEFAULT_REQUEST_INFO, {})
        now = datetime.datetime.fromtimestamp(int(time.time())) # Remove milliseconds as MySQL do
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )

        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WSS.LocalReservedStatus(reservation1_id, CoordAddress.translate(self.lab_address), lab_session_id, { 'address' : 'server:inst@mach' }, 30, '{}', now, now, True, 30, 'http://www.weblab.deusto.es/weblab/client/adfas')

        self.assertTrue(hasattr(status, 'timestamp_before'),  "Unexpected status. Expected\n %s\n, but the obtained does not have timestamp_before:\n %s\n" % (expected_status, status))
        self.assertTrue(status.timestamp_before >= now and status.timestamp_before <= now + datetime.timedelta(seconds=10),
                        "Unexpected status due to timestamp_before: %s; expected something like %s" % (status, expected_status))
        self.assertTrue(status.timestamp_after  >= now and status.timestamp_after  <= now + datetime.timedelta(seconds=10),
                        "Unexpected status due to timestamp_after: %s; expected something like %s" % (status, expected_status))

        status.timestamp_before = now
        status.timestamp_after = now
        self.assertEquals( expected_status, status )

    def test_reject_experiment_laboratory_raises_exception(self):
        mock_laboratory = self.mocker.mock()
        mock_laboratory.reserve_experiment(ExperimentInstanceId('inst1','exp1','cat1'), '"sample initial data"', mocker.ANY)
        self.mocker.throw( Exception("Any unhandled exception") )

        self.mock_locator[coord_addr(self.lab_address)]
        self.mocker.result(mock_laboratory)


        self.mocker.replay()
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5, True, 'sample initial data', DEFAULT_REQUEST_INFO, {})
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )

        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WSS.WaitingInstancesQueueStatus(reservation1_id, 0)
        self.assertEquals( expected_status, status )

    def test_reject_experiment_voodoo_gen_raises_exception(self):
        self.mock_locator[coord_addr(self.lab_address)]
        self.mocker.throw( Exception("Unhandled exception") )

        self.mocker.replay()
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5, True, 'sample initial data', DEFAULT_REQUEST_INFO, {})
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )

        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WSS.WaitingInstancesQueueStatus(reservation1_id, 0)
        self.assertEquals( expected_status, status )


def suite():
    return unittest.makeSuite(ConfirmerTestCase)

if __name__ == '__main__':
    unittest.main()

