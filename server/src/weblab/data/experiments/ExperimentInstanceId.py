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

import weblab.data.experiments.ExperimentId as ExperimentId

class ExperimentInstanceId(object):
    def __init__(self, inst_name, exp_name, cat_name):
        self.inst_name = inst_name
        self.exp_name  = exp_name
        self.cat_name  = cat_name

    def to_experiment_id(self):
        return ExperimentId.ExperimentId(self.exp_name, self.cat_name)

    def to_weblab_str(self):
        return "%s:%s@%s" % (self.inst_name, self.exp_name, self.cat_name)

    def __eq__(self, other):
        return ( isinstance(other, ExperimentInstanceId) 
                and self.inst_name == other.inst_name
                and self.exp_name  == other.exp_name
                and self.cat_name  == other.cat_name
            )

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __hash__(self):
        return hash(self.inst_name) * 31 ** 3 + hash(self.exp_name) * 31 ** 2 + hash(self.cat_name) * 31 + hash("ExperimentInstanceId")

    def __repr__(self):
        return "<ExperimentInstanceId inst_name=%s; exp_name=%s; cat_name=%s />" % (
                    self.inst_name,
                    self.exp_name,
                    self.cat_name
                )

