#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005 onwards University of Deusto
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
from __future__ import print_function, unicode_literals

from voodoo.representable import Representable

class Resource(object):
    __metaclass__ = Representable

    def __init__(self, resource_type, resource_instance):
        self.resource_type     = resource_type
        self.resource_instance = resource_instance

    def to_weblab_str(self):
        return "%s@%s" % (self.resource_instance, self.resource_type)

    def __hash__(self):
        return hash(self.to_weblab_str())

    @staticmethod
    def parse(weblab_str):
        pos = weblab_str.find("@")
        resource_instance = weblab_str[:pos]
        resource_type     = weblab_str[pos + 1 :]
        return Resource(resource_type, resource_instance)

