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


import unittest

from weblab.core.coordinator.resource import Resource

class ResourceTest(unittest.TestCase):

    def test_eq_simple(self):
        res1 = Resource("foo", "bar")
        res2 = Resource("foo", "bar")
        self.assertEquals(res1, res2)

    def test_eq_none(self):
        res1 = Resource(None, None)
        res2 = Resource(None, None)
        self.assertEquals(res1, res2)

    def test_eq_other(self):
        res1 = Resource("foo", "bar")
        res2 = Resource("foo", "bar2")
        self.assertNotEquals(res1, res2)

        res2 = Resource("foo2", "bar")
        self.assertNotEquals(res1, res2)

        res2 = "foobar"
        self.assertNotEquals(res1, res2)

    def test_repr(self):
        res1 = Resource("foo","bar")
        res2 = eval(repr(res1))
        self.assertEquals(res1, res2)

def suite():
    return unittest.makeSuite(ResourceTest)

if __name__ == '__main__':
    unittest.main()

