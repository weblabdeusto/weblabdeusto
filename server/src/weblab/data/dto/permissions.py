#!/usr/bin/python
# -*- coding: utf-8 -*-
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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

class Permission(object):
    """
    DTO for a Permission object
    """

    def __init__(self, name):
        super(Permission, self).__init__()
        self.name = name
        self.parameters = []

    def add_parameter(self, parameter):
        self.parameters.append(parameter)

    def get_parameter_value(self, name, default_value = None):
        for param in self.parameters:
            if param.name == name:
                return param.value
        return default_value

    def __repr__(self):
        return "Permission(name = %r, parameters = %r)" % (
                self.name,
                self.parameters
            )


class PermissionType(object):
    """
    DTO for a PermissionType object
    """

    def __init__(self, name, description):
        super(PermissionType, self).__init__()
        self.name = name
        self.description = description

    def __repr__(self):
        return "PermissionType(name = %r, description = %r)" % (
                self.name,
                self.description,
            )


class PermissionParameter(object):
    """
    DTO for a PermissionParameter object
    """

    def __init__(self, name, datatype, value):
        super(PermissionParameter, self).__init__()
        self.name = name
        self.datatype = datatype
        self.value = value

    def __repr__(self):
        return "PermissionParameter(name = %r, datatype = %r, value = %r)" % (
                self.name,
                self.datatype,
                self.value
            )

