#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# Author: Pablo Orduña <pablo.orduna@deusto.es>
#
from __future__ import print_function, unicode_literals

import unittest
import datetime

from weblab.data.dto.experiments import Experiment, ExperimentCategory, ExperimentUse, ExperimentAllowed, ExperimentClient


class ExperimentsTestCase(unittest.TestCase):

    def setUp(self):
        self.category   = ExperimentCategory("Dummy experiments")
        self.client     = ExperimentClient("client", {})
        self.experiment = Experiment("ud-dummy", self.category, datetime.datetime.now(), datetime.datetime.now(), self.client, 5L)
        self.use        = ExperimentUse(datetime.datetime.now(), datetime.datetime.now(), self.experiment, 'student1', '127.0.0.1', 5L)
        self.allowed    = ExperimentAllowed(self.experiment, 150, 5, True, 'exp::user', 1, 'user')

    def _check_repr(self, obj):
        self.assertEquals(repr(obj), repr(eval(repr(obj))))

    def test_experiment(self):
        self._check_repr(self.experiment)

    def test_experiment_category(self):
        self._check_repr(self.category)

    def test_experiment_use(self):
        self._check_repr(self.use)

    def test_experiment_allowed(self):
        self._check_repr(self.allowed)


def suite():
    return unittest.makeSuite(ExperimentsTestCase)

if __name__ == '__main__':
    unittest.main()
