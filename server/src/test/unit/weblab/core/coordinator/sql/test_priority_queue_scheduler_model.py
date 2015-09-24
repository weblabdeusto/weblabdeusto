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
import weblab.core.coordinator.sql.priority_queue_scheduler_model as PQSM
import weblab.core.coordinator.sql.model as CM

class PriorityQueueSchedulerModelTestCase(unittest.TestCase):

    def test_repr_pq_current_reservation(self):
        resource_type     = CM.ResourceType("foo")
        resource_instance = CM.ResourceInstance(resource_type, "instance")
        current_resource_slot = CM.CurrentResourceSlot(resource_instance)
        slot_reservation = CM.SchedulingSchemaIndependentSlotReservation(current_resource_slot)

        experiment_type = CM.ExperimentType("exp", "cat")
        reservation     = CM.Reservation("hola", "{}", "{}", "{}", None)
        reservation.experiment_type = experiment_type
        current_reservation = CM.CurrentReservation("hola")

        concrete_current_reservation = PQSM.ConcreteCurrentReservation(slot_reservation, current_reservation.id, 50, 100, 1, True)

        repr(concrete_current_reservation) # No exception is raised

    def test_repr_pq_waiting_reservation(self):
        resource_type         = CM.ResourceType("foo")
        experiment_type = CM.ExperimentType("exp", "cat")
        reservation     = CM.Reservation("hola", "{}", "{}", "{}", None)
        reservation.experiment_type = experiment_type

        pq_waiting_reservation = PQSM.WaitingReservation(resource_type, reservation.id, 50, 1, True)

        repr(pq_waiting_reservation) # No exception is raised

def suite():
    return unittest.makeSuite(PriorityQueueSchedulerModelTestCase)

if __name__ == '__main__':
    unittest.main()
