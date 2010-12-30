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
# Author: Pablo Orduña <pablo@ordunya.com>
#

class Resource(object):
    def __init__(self, resource_type, resource_instance):
        self.resource_type     = resource_type
        self.resource_instance = resource_instance

    def __eq__(self, other):
        if not isinstance(other, Resource):
            return False
        return self.resource_type == other.resource_type and self.resource_instance == other.resource_instance

    def __repr__(self):
        return "Resource(%s, %s)" % (repr(self.resource_type), repr(self.resource_instance))

