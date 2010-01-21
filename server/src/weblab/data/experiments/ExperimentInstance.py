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

class ExperimentInstance(object):
    def __init__(self, name, owner, experiment, laboratory, start_date, end_date):
        super(ExperimentInstance,self).__init__()
        self.name       = name
        self.owner      = owner
        self.experiment = experiment
        self.laboratory = laboratory
        self.start_date = start_date
        self.end_date   = end_date
    def __repr__(self):
        return "<ExperimentInstance: name: %s; owner: %s; experiment: %s; laboratory: %s; start_date: %s; end_date: %s>" % (
                self.name,
                self.owner,
                self.experiment,
                self.laboratory,
                self.start_date,
                self.end_date
            )

    def get_experiment_instance_id(self):
        return ExperimentInstanceId.ExperimentInstanceId(
                self.name, self.experiment.name, self.experiment.category.name
            )
