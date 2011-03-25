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

import datetime
import unittest
import weblab.user_processing.coordinator.CoordinatorModel as CM

class CoordinatorModelTestCase(unittest.TestCase):

    def test_repr_resource_type(self):
        repr(CM.ResourceType("foo")) # No exception is raised

    def test_repr_resource_instance(self):
        resource_type = CM.ResourceType("foo")
        repr(CM.ResourceInstance(resource_type, "foo")) # No exception is raised

    def test_repr_current_resource_slot(self):
        resource_type     = CM.ResourceType("foo")
        resource_instance = CM.ResourceInstance(resource_type, "instance")
        repr(CM.CurrentResourceSlot(resource_instance)) # No exception is raised

    def test_repr_scheduling_schema_independent_slot_reservation(self):
        resource_type         = CM.ResourceType("foo")
        resource_instance     = CM.ResourceInstance(resource_type, "instance")
        current_resource_slot = CM.CurrentResourceSlot(resource_instance)
        repr(CM.SchedulingSchemaIndependentSlotReservation(current_resource_slot)) # No exception is raised

    def test_repr_experiment_type(self):
        experiment_type = CM.ExperimentType("exp", "cat")
        repr(experiment_type) # No exception is raised

    def test_repr_experiment_instance(self):
        experiment_type     = CM.ExperimentType("exp", "cat")
        experiment_instance = CM.ExperimentInstance(experiment_type, "lab:inst@mach", "exp1")
        repr(experiment_instance) # No exception is raised

    def test_repr_reservation(self):
        experiment_type = CM.ExperimentType("exp", "cat")
        reservation     = CM.Reservation("hola", "{}", "{}", None)
        reservation.experiment_type = experiment_type
        repr(reservation) # No exception is raised

    def test_repr_current_reservation(self):
        experiment_type = CM.ExperimentType("exp", "cat")
        reservation     = CM.Reservation("hola", "{}", "{}", None)
        reservation.experiment_type = experiment_type
        current_reservation = CM.CurrentReservation("hola")
        repr(current_reservation) # No exception is raised

    def test_repr_batch_retrieved_data(self):
        batch_retrieved_data = CM.BatchRetrievedData("foobar", datetime.datetime.now(), "exp1:inst@mach", "{}")
        repr(batch_retrieved_data) # No exception is raised

def suite():
    return unittest.makeSuite(CoordinatorModelTestCase)

if __name__ == '__main__':
    unittest.main()
