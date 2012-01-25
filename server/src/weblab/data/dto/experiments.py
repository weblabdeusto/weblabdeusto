#!/usr/bin/python
# -*- coding: utf-8 -*-
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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

from weblab.data.experiments import ExperimentInstanceId
from weblab.data.experiments import ExperimentId
from voodoo.representable import Representable

class ExperimentCategory(object):

    __metaclass__ = Representable

    def __init__(self, name):
        super(ExperimentCategory,self).__init__()
        self.name = unicode(name)

class Experiment(object):

    __metaclass__ = Representable

    def __init__(self, name, category, start_date, end_date, id=None):
        super(Experiment,self).__init__()

        self.name       = unicode(name)
        self.category   = category
        self.start_date = start_date
        self.end_date   = end_date
        self.id         = id

    def get_experiment_instance_id(self):
        return ExperimentInstanceId(None, self.name, self.category.name)

    def to_experiment_id(self):
        return ExperimentId(self.name, self.category.name)

    def get_unique_name(self):
        return self.name + "@" + self.category.name

class ExperimentUse(object):

    __metaclass__ = Representable

    def __init__(self, start_date, end_date, experiment, agent, origin, id=None):

        self.start_date = start_date
        self.end_date   = end_date
        self.experiment = experiment
        self.agent      = agent # User or ExternalEntity
        self.origin     = origin
        self.id         = id


DEFAULT_PRIORITY = 5
DEFAULT_INITIALIZATION_IN_ACCOUNTING = True

class ExperimentAllowed(object):

    __metaclass__ = Representable

    def __init__(self, experiment, time_allowed, priority, initialization_in_accounting):

        super(ExperimentAllowed,self).__init__()
        self.experiment                   = experiment
        self.time_allowed                 = time_allowed
        self.priority                     = priority
        self.initialization_in_accounting = initialization_in_accounting


