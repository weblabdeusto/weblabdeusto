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
import pmock

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.locator.EasyLocator      as EasyLocator
import voodoo.sessions.SessionId           as SessionId

import test.unit.configuration as configuration_module
import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.data.ServerType as ServerType
import weblab.methods as weblab_methods
from weblab.data.experiments.ExperimentInstanceId import ExperimentInstanceId
from weblab.data.experiments.ExperimentId import ExperimentId
import weblab.user_processing.coordinator.Coordinator as Coordinator

import weblab.user_processing.coordinator.WebLabQueueStatus as WQS

class MockLocator(object):
    def __init__(self):
        self.real_mock = None
        # This way, a MockLocator is passed to the Confirmer,
        # and then each test will rewrite the "_real_mock"
        # attribute as needed

    def retrieve_methods(self, server_type):
        return getattr(weblab_methods, server_type.name)

    def get_server_from_coord_address(self, *args):
        return self.real_mock.get_server_from_coordaddress( *args )

def coord_addr(coord_addr_str):
    return CoordAddress.CoordAddress.translate_address( coord_addr_str )

class ConfirmerTestCase(unittest.TestCase):
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
        self.coordinator.add_experiment_instance_id(self.lab_address, ExperimentInstanceId('inst1', 'exp1','cat1'))

    def test_free_experiment_success(self):
        mock_laboratory = pmock.Mock()
        mock_laboratory.expects(
                pmock.once()
            ).free_experiment( pmock.eq('lab_session_id') )

        self.mock_locator.real_mock = pmock.Mock()
        self.mock_locator.real_mock.expects(
                pmock.once()
            ).get_server_from_coordaddress(
                pmock.eq(self.coord_address), pmock.eq(coord_addr(self.lab_address)), pmock.eq(ServerType.Laboratory), pmock.eq('all')
            ).will( pmock.return_value( (mock_laboratory,) ) )


        self.confirmer.enqueue_free_experiment(self.lab_address, 'lab_session_id')
        self.confirmer._free_handler.join()

        mock_laboratory.verify()

    def test_free_experiment_raises_exception(self):
        self.mock_locator.real_mock = pmock.Mock()
        self.mock_locator.real_mock.expects(
                pmock.once()
            ).get_server_from_coordaddress(
                pmock.eq(self.coord_address), pmock.eq(coord_addr(self.lab_address)), pmock.eq(ServerType.Laboratory), pmock.eq('all')
            ).will( pmock.raise_exception( Exception('foo') ) )

        self.confirmer.enqueue_free_experiment(self.lab_address, 'lab_session_id')
        self.confirmer._free_handler.join()

        self.assertEquals( None, self.confirmer._free_handler.raised_exc )

    def test_confirm_experiment(self):
        lab_session_id = SessionId.SessionId("samplesession_id")

        mock_laboratory = pmock.Mock()
        mock_laboratory.expects(
                pmock.once()
            ).reserve_experiment(
                pmock.eq(ExperimentInstanceId('inst1','exp1','cat1'))
            ).will( pmock.return_value( lab_session_id ) )

        self.mock_locator.real_mock = pmock.Mock()
        self.mock_locator.real_mock.expects(
                pmock.once()
            ).get_server_from_coordaddress(
                pmock.eq(self.coord_address), pmock.eq(coord_addr(self.lab_address)), pmock.eq(ServerType.Laboratory), pmock.eq('all')
            ).will( pmock.return_value( (mock_laboratory,) ) )

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5)
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )
        
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WQS.ReservedQueueStatus(CoordAddress.CoordAddress.translate_address(self.lab_address), lab_session_id, 30)
        self.assertEquals( expected_status, status )

    def test_reject_experiment_laboratory_raises_exception(self):
        mock_laboratory = pmock.Mock()
        mock_laboratory.expects(
                pmock.once()
            ).reserve_experiment(
                pmock.eq(ExperimentInstanceId('inst1','exp1','cat1'))
            ).will( pmock.raise_exception( Exception("Any unhandled exception") ) )

        self.mock_locator.real_mock = pmock.Mock()
        self.mock_locator.real_mock.expects(
                pmock.once()
            ).get_server_from_coordaddress(
                pmock.eq(self.coord_address), pmock.eq(coord_addr(self.lab_address)), pmock.eq(ServerType.Laboratory), pmock.eq('all')
            ).will( pmock.return_value( (mock_laboratory,) ) )

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5)
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )
        
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WQS.WaitingInstancesQueueStatus(0)
        self.assertEquals( expected_status, status )

    def test_reject_experiment_voodoo_gen_raises_exception(self):
        self.mock_locator.real_mock = pmock.Mock()
        self.mock_locator.real_mock.expects(
                pmock.once()
            ).get_server_from_coordaddress(
                pmock.eq(self.coord_address), pmock.eq(coord_addr(self.lab_address)), pmock.eq(ServerType.Laboratory), pmock.eq('all')
            ).will( pmock.raise_exception( Exception("Unhandled exception") ) )

        status, reservation1_id = self.coordinator.reserve_experiment(ExperimentId('exp1','cat1'), 30, 5)
        self.coordinator.confirmer._confirm_handler.join()
        self.assertEquals( None, self.confirmer._confirm_handler.raised_exc )
        
        status = self.coordinator.get_reservation_status(reservation1_id)
        expected_status =  WQS.WaitingInstancesQueueStatus(0)
        self.assertEquals( expected_status, status )


def suite():
    return unittest.makeSuite(ConfirmerTestCase)

if __name__ == '__main__':
    unittest.main()

