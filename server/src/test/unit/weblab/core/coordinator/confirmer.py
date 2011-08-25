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
import mocker

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.locator.EasyLocator      as EasyLocator
import voodoo.sessions.session_id           as SessionId

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

import weblab.data.ServerType as ServerType
import weblab.methods as weblab_methods
from weblab.data.experiments import ExperimentInstanceId
from weblab.data.experiments import ExperimentId
from weblab.core.coordinator.resource import Resource

import weblab.core.coordinator.coordinator as Coordinator

import weblab.core.coordinator.status as WSS

class MockLocator(object):
    
    def __init__(self):
        self.real_mock = None
        # This way, a MockLocator is passed to the Confirmer,
        # and then each test will rewrite the "_real_mock"
        # attribute as needed

    def retrieve_methods(self, server_type):
        return getattr(weblab_methods, server_type)

    def get_server_from_coord_address(self, *args):
        return self.real_mock.get_server_from_coordaddress( *args )

def coord_addr(coord_addr_str):
    return CoordAddress.CoordAddress.translate_address( coord_addr_str )

DEFAULT_REQUEST_INFO = {'facebook' : False, 'mobile' : False}

class ConfirmerTestCase(mocker.MockerTestCase):
    
    def setUp(self):

        self.coord_address = CoordAddress.CoordAddress.translate_address(
                "server0:instance0@machine0"
            )

        self.mock_locator  = MockLocator()
        self.locator       = EasyLocator.EasyLocator( self.coord_address, self.mock_locator )

        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.coordinator = Coordinator.Coordinator(self.locator, self.cfg_manager)
        self.coordinator._clean()
        self.confirmer   = self.coordinator.confirmer

        self.lab_address = u"lab1:inst@machine"
        self.coordinator.add_experiment_instance_id(self.lab_address, ExperimentInstanceId('inst1', 'exp1','cat1'), Resource("res_type", "res_inst"))

    def test_free_experiment_success(self):
        mock_laboratory = self.mocker.mock()
        mock_laboratory.free_experiment('lab_session_id')
        
        self.mock_locator.real_mock = self.mocker.mock()
        self.mock_locator.real_mock.get_server_from_coordaddress(
                self.coord_address,
                coord_addr(self.lab_address),
                ServerType.Laboratory,
                'all'
        )
        self.mocker.result((mock_laboratory,))

        self.mocker.replay()
        self.confirmer.enqueue_free_experiment(self.lab_address, '5', 'lab_session_id', ExperimentInstanceId('inst1','exp1','cat1'))
        self.confirmer._free_handler.join()

    def test_free_experiment_raises_exception(self):
        self.mock_locator.real_mock = self.mocker.mock()
        self.mock_locator.real_mock.get_server_from_coordaddress(
                self.coord_address,
                coord_addr(self.lab_address),
                ServerType.Laboratory,
                'all'
        )
        self.mocker.throw( Exception('foo') )

        self.mocker.replay()
        self.confirmer.enqueue_free_experiment(self.lab_address, '5', 'lab_session_id', ExperimentInstanceId('inst1','exp1','cat1'))
        self.confirmer._free_handler.join()

        self.assertEquals( None, self.confirmer._free_handler.raised_exc )

    def test_confirm_experiment(self):
        lab_session_id = SessionId.SessionId("samplesession_id")

        mock_laboratory = self.mocker.mock()
        mock_laboratory.reserve_experiment(ExperimentInstanceId('inst1','exp1','cat1'), '"sample initial data"', mocker.ANY)
        self.mocker.result((lab_session_id, None, 'server:inst@mach'))

        self.mock_locator.real_mock = self.mocker.mock()
        self.mock_locator.real_mock.get_server_from_coordaddress(
                self.coord_address,
                coord_addr(self.lab_address),
                ServerType.Laboratory,
                'all'
        )
        self.mocker.result((mock_laboratory,))

        self.mocker.replay()
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5, 'sample initial data', DEFAULT_REQUEST_INFO)
        now = datetime.datetime.fromtimestamp(int(time.time())) # Remove milliseconds as MySQL do
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )
        
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WSS.ReservedStatus(CoordAddress.CoordAddress.translate_address(self.lab_address), lab_session_id, 30, '{}', now, now)

        self.assertTrue("Unexpected status due to timestamp_before: %s; expected something like %s" % (status, expected_status), 
                            status.timestamp_before >= now and status.timestamp_before <= now + datetime.timedelta(seconds=10))
        self.assertTrue("Unexpected status due to timestamp_after: %s; expected something like %s" % (status, expected_status),
                            status.timestamp_after  >= now and status.timestamp_after  <= now + datetime.timedelta(seconds=10))

        status.timestamp_before = now
        status.timestamp_after = now
        self.assertEquals( expected_status, status )

    def test_reject_experiment_laboratory_raises_exception(self):
        mock_laboratory = self.mocker.mock()
        mock_laboratory.reserve_experiment(ExperimentInstanceId('inst1','exp1','cat1'), '"sample initial data"', mocker.ANY)
        self.mocker.throw( Exception("Any unhandled exception") )

        self.mock_locator.real_mock = self.mocker.mock()
        self.mock_locator.real_mock.get_server_from_coordaddress(
                self.coord_address,
                coord_addr(self.lab_address),
                ServerType.Laboratory,
                'all'
        )
        self.mocker.result((mock_laboratory,))

        self.mocker.replay()
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5, 'sample initial data', DEFAULT_REQUEST_INFO)
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )
        
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WSS.WaitingInstancesQueueStatus(0)
        self.assertEquals( expected_status, status )

    def test_reject_experiment_voodoo_gen_raises_exception(self):
        self.mock_locator.real_mock = self.mocker.mock()
        self.mock_locator.real_mock.get_server_from_coordaddress(
                self.coord_address,
                coord_addr(self.lab_address),
                ServerType.Laboratory,
                'all'
        )
        self.mocker.throw( Exception("Unhandled exception") )

        self.mocker.replay()
        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5, 'sample initial data', DEFAULT_REQUEST_INFO)
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )
        
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WSS.WaitingInstancesQueueStatus(0)
        self.assertEquals( expected_status, status )


def suite():
    return unittest.makeSuite(ConfirmerTestCase)

if __name__ == '__main__':
    unittest.main()

