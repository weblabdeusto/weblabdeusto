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

class ExperimentCategory(object):
    def __init__(self, name):
        super(ExperimentCategory,self).__init__()
        self.name = name
    def __repr__(self):
        return 'ExperimentCategory(name=%r)' % self.name

class Experiment(object):
    
    def __init__(self, name, category, start_date, end_date, id=None):
        super(Experiment,self).__init__()
        self.id         = id
        self.name       = name
        self.category   = category
        self.start_date = start_date
        self.end_date   = end_date

    def __repr__(self):
        return 'Experiment(name=%r, category=%r, start_date=%r, end_date=%r)' % (
                self.name,
                self.category,
                self.start_date,
                self.end_date
            )

    def get_experiment_instance_id(self):
        return ExperimentInstanceId(None, self.name, self.category.name)

    def to_experiment_id(self):
        return ExperimentId(self.name, self.category.name)

    def get_unique_name(self):
        return self.name + "@" + self.category.name

class ExperimentUse(object):
    
    def __init__(self, start_date, end_date, experiment, agent, origin, id=None):
        self.id         = id
        self.start_date = start_date
        self.end_date   = end_date
        self.experiment = experiment
        self.agent      = agent # User or ExternalEntity
        self.origin     = origin

    def __repr__(self):
        return u"ExperimentUse(start_date = %r, end_date = %r, experiment = %r, agent = %r, origin = %r, id = %r)" % (
                self.start_date,
                self.end_date,
                self.experiment,
                self.agent,
                self.origin,
                self.id
            )

DEFAULT_PRIORITY = 5
DEFAULT_INITIALIZATION_IN_ACCOUNTING = True

class ExperimentAllowed(object):
    def __init__(self, experiment, time_allowed, priority, initialization_in_accounting):
        super(ExperimentAllowed,self).__init__()
        self.experiment                   = experiment
        self.time_allowed                 = time_allowed
        self.priority                     = priority
        self.initialization_in_accounting = initialization_in_accounting

    def __repr__(self):
        return "ExperimentAllowed(experiment = %r, time_allowed = %r, priority = %r, initialization_in_accounting = %r)" % (self.experiment, self.time_allowed, self.priority, self.initialization_in_accounting)

