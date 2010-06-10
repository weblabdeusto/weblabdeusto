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

class ExperimentAllowed(object):
    def __init__(self, experiment, time_allowed):
        super(ExperimentAllowed,self).__init__()
        self.experiment   = experiment
        self.time_allowed = time_allowed

    def __repr__(self):
        return "<ExperimentAllowed: experiment = %s; time_allowed = %s>" % (self.experiment, self.time_allowed)

