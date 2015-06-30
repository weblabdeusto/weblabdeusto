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

import cPickle as pickle
import unittest
import weblab.core.coordinator.sql.externals.weblabdeusto_scheduler_model as WLDM

class WebLabDeustoModelTestCase(unittest.TestCase):

    def test_repr_external_reservation(self):
        repr(WLDM.ExternalWebLabDeustoReservation("foo", "bar", "", 5.0)) # No exception is raised

    def test_repr_external_pending_results(self):
        repr(WLDM.ExternalWebLabDeustoReservationPendingResults("reservation_id", "remote_reservation_id", "resource_type_name", "route1", "{}", pickle.dumps({}), "ud-logic@General experiments")) # No exception is raised


def suite():
    return unittest.makeSuite(WebLabDeustoModelTestCase)

if __name__ == '__main__':
    unittest.main()
