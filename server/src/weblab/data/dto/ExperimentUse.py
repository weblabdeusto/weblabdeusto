#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

class ExperimentUse(object):
    
    def __init__(self):
        self.id         = None
        self.start_date = None
        self.end_date   = None
        self.experiment = None
        self.agent      = None # User or ExternalEntity
        self.origin     = u"unknown"

    def __repr__(self):
        return u"ExperimentUse(id = %i, start_date = '%s', end_date = '%s', experiment = %r, agent = %r, origin = '%s')" % (
                self.id,
                self.start_date,
                self.end_date,
                self.experiment,
                self.agent,
                self.origin
            ) 