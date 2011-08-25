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
# 

from weblab.data.experiments import ExperimentInstanceId
from weblab.data.experiments import ExperimentId

class Experiment(object):
    
    def __init__(self, name, category, start_date, end_date, id=None):
        super(Experiment,self).__init__()
        self.id         = id
        self.name       = name
        self.category   = category
        self.start_date = start_date
        self.end_date   = end_date

    def __repr__(self):
        return '<Experiment name="%s" category="%s" start_date="%s" end_date="%s">' % (
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