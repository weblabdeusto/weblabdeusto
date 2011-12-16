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

import unittest

from voodoo.representable import Representable

class DirectClass(Representable):
    def __init__(self, a, b):
        self.a = a
        self.b = b

class ChildClass(DirectClass):
    def __init__(self, a, b, c):
        super(ChildClass, self).__init__(a, b)
        self.c = c

class GrandChildClass(ChildClass):
    pass

class RepresentableTestCase(unittest.TestCase):

    def test_equality(self):
        self.assertEquals(DirectClass(5,6), DirectClass(5,6))
        self.assertNotEquals(DirectClass(5,6), DirectClass(6,5))

    def test_repr(self):
        self.assertEquals(DirectClass(5,6), eval(repr(DirectClass(5,6))))
        self.assertNotEquals(DirectClass(6,5), eval(repr(DirectClass(5,6))))

    def test_child_equality(self):
        self.assertEquals(ChildClass(5,6,7), ChildClass(5,6,7))
        self.assertNotEquals(ChildClass(5,6,7), ChildClass(5,6,8))
        self.assertNotEquals(ChildClass(5,6,7), ChildClass(6,5,7))

    def test_child_repr(self):
        self.assertEquals(ChildClass(5,6,7), eval(repr(ChildClass(5,6,7))))
        self.assertNotEquals(ChildClass(6,5,7), eval(repr(ChildClass(5,6,7))))
       
    def test_grand_child_equality(self):
        self.assertEquals(GrandChildClass(5,6,7), GrandChildClass(5,6,7))
        self.assertNotEquals(GrandChildClass(5,6,7), GrandChildClass(5,6,8))
        self.assertNotEquals(GrandChildClass(5,6,7), GrandChildClass(6,5,7))
        self.assertNotEquals(GrandChildClass(5,6,7), ChildClass(5,6,7))

    def test_grand_child_repr(self):
        self.assertEquals(GrandChildClass(5,6,7), eval(repr(GrandChildClass(5,6,7))))
        self.assertNotEquals(GrandChildClass(6,5,7), eval(repr(GrandChildClass(5,6,7))))

def suite():
    return unittest.makeSuite(RepresentableTestCase)

if __name__ == '__main__':
    unittest.main()

