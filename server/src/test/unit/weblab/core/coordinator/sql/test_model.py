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

import datetime
import unittest
import weblab.core.coordinator.sql.model as CM

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

    def test_repr_active_reservation_scheduler(self):
        resource_type = CM.ResourceType("foo")
        experiment_type     = CM.ExperimentType("exp", "cat")
        assoc = CM.ActiveReservationSchedulerAssociation('foo', experiment_type, resource_type)
        repr(assoc) # No exception

    def test_repr_reservation(self):
        experiment_type = CM.ExperimentType("exp", "cat")
        reservation     = CM.Reservation("hi", "{}", "{}", "{}", None)
        reservation.experiment_type = experiment_type
        repr(reservation) # No exception is raised

    def test_repr_current_reservation(self):
        experiment_type = CM.ExperimentType("exp", "cat")
        reservation     = CM.Reservation("hi", "{}", "{}", "{}", None)
        reservation.experiment_type = experiment_type
        current_reservation = CM.CurrentReservation("hi")
        repr(current_reservation) # No exception is raised

    def test_repr_pending_to_finish_reservation(self):
        pending_reservation = CM.PendingToFinishReservation("hi")
        repr(pending_reservation) # No exception is raised

    def test_repr_post_reservation_retrieved_data(self):
        post_reservation_retrieved_data = CM.PostReservationRetrievedData("foobar", True, datetime.datetime.now(), datetime.datetime.now(), "{}", "{}")
        repr(post_reservation_retrieved_data) # No exception is raised

def suite():
    return unittest.makeSuite(CoordinatorModelTestCase)

if __name__ == '__main__':
    unittest.main()
