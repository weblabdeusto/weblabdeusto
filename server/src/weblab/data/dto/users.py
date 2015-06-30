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
#
from __future__ import print_function, unicode_literals

class User(object):

    def __init__(self, login, full_name, email, role):
        super(User,self).__init__()
        self.login = login
        self.full_name = full_name
        self.email = email
        self.role = role

    def __repr__(self):
        return "User(login = %r, full_name = %r, email = %r, role = %r)" % (
                self.login,
                self.full_name,
                self.email,
                self.role
            )

class Group(object):

    def __init__(self, name, id=None):
        super(Group, self).__init__()
        self.id = id
        self.name = name
        self._parent = None
        self.children = []

    def add_child(self, child):
        child._parent = self
        self.children.append(child)

    def set_children(self, children):
        for child in children:
            self.add_child(child)

    def get_full_name(self):
        if self._parent is None:
            return self.name
        else:
            return self._parent.get_full_name() + " > " + self.name

    def __repr__(self):
        return "Group(id = %i, full_name = %r)" % (
                self.id,
                self.get_full_name()
            )

class Role(object):

    def __init__(self, name):
        super(Role, self).__init__()
        self.name = name

    def __repr__(self):
        return "Role(name = %r)" % (
                self.name
            )

class StudentRole(Role):
    def __init__(self):
        super(StudentRole, self).__init__('student')
