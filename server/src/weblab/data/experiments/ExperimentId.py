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

class ExperimentId(object):
    def __init__(self, exp_name, cat_name):
        self.exp_name  = exp_name
        self.cat_name  = cat_name

    def __eq__(self, other):
        return ( isinstance(other, ExperimentId) 
                and self.exp_name  == other.exp_name
                and self.cat_name  == other.cat_name
            )
    
    def __cmp__(self, other):
        if isinstance(other, ExperimentId):
            return -1
        elif self.exp_name != other.exp_name:
            return cmp(self.exp_name, other.exp_name)
        else:
            return cmp(self.cat_name, other.cat_name)

    def __repr__(self):
        return "<ExperimentId exp_name=%s; cat_name=%s />" % (
                    self.exp_name,
                    self.cat_name
                )
    
    def to_dict(self):
        return {'exp_name': self.exp_name, 'cat_name': self.cat_name}

