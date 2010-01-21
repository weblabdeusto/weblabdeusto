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

import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.data.experiments.ExperimentId as ExperimentId

class Experiment(object):
    def __init__(self, name, owner, category, start_date, end_date):
        super(Experiment,self).__init__()
        self.name       = name
        self.owner      = owner
        self.category   = category
        self.start_date = start_date
        self.end_date   = end_date

    def __repr__(self):
        return '<Experiment name="%s" owner="%s" category="%s" start_date="%s" end_date="%s">' % (
                self.name,
                self.owner,
                self.category,
                self.start_date,
                self.end_date
            )

    def get_experiment_instance_id(self):
        return ExperimentInstanceId.ExperimentInstanceId(None, self.name, self.category.name)

    def to_experiment_id(self):
        return ExperimentId.ExperimentId(self.name, self.category.name)
