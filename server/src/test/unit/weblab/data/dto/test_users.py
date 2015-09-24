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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import unittest

import weblab.data.dto.users as Group


class GroupTestCase(unittest.TestCase):

    def test_get_full_name(self):
        group1 = Group.Group("group 1")
        group12 = Group.Group("group 1.2")
        group121 = Group.Group("group 1.2.1")
        group12.add_child(group121)
        group1.add_child(group12)

        self.assertEquals(group1.get_full_name(), "group 1")
        self.assertEquals(group12.get_full_name(), "group 1 > group 1.2")
        self.assertEquals(group121.get_full_name(), "group 1 > group 1.2 > group 1.2.1")

def suite():
    return unittest.makeSuite(GroupTestCase)

if __name__ == '__main__':
    unittest.main()