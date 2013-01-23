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

    def __repr__(self):
        return "Permission(name = '%s', parameters = '%r')" % (
                self.name,
                self.parameters
            )


class PermissionType(object):
    """
    DTO for a PermissionType object
    """

    def __init__(self, name, description, user_applicable, role_applicable):
        super(PermissionType, self).__init__()
        self.name = name
        self.description = description
        self.user_applicable = user_applicable
        self.role_applicable = role_applicable

    def __repr__(self):
        return "PermissionType(name = '%s', description = '%s', user_applicable = '%r', role_applicable = '%r')" % (
                self.name,
                self.description,
                self.user_applicable,
                self.role_applicable
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
        return "PermissionParameter(name = '%s', datatype = '%s', value = '%s')" % (
                self.name,
                self.datatype,
                self.value
            )

