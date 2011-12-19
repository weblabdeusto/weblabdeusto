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

from abc import ABCMeta, abstractmethod
from voodoo.representable import Representable, AbstractRepresentable

#########################################################
# 
# Regular scenario: parent class is representable,
# the inherited classes are also representable.
# 

class DirectClass(object):

    __metaclass__ = Representable

    def __init__(self, a, b):
        self.a = a
        self.b = b

class ChildClass(DirectClass):
    def __init__(self, a, b, c):
        super(ChildClass, self).__init__(a, b)
        self.c = c

class GrandChildClass(ChildClass):
    pass

###########################################################
# 
# Wrong case: the constructor does not set a field that
# appears in the constructor of the class. This should 
# fail when creating the object.
# 

class WrongClass(object):

    __metaclass__ = Representable

    def __init__(self, a, b, missing_field):
        self.a = a
        self.b = b
        # No field called "missing_field"

#############################################################
# 
# Abstract class: enable classes to be abstract and 
# representables at the very same time.
# 

class AbstractClass(object):

    __metaclass__ = AbstractRepresentable

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @abstractmethod
    def method(self):
        pass

class ConcreteClass(AbstractClass):
    def __init__(self, a, b, c):
        super(ConcreteClass, self).__init__(a,b)
        self.c = c

    def method(self):
        pass

##############################################################
# 
# Abstract class: enable a class to be abstract, and then
# a derived class to be representable
# 

class PureAbstractClass(object):
    __metaclass__ = ABCMeta

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @abstractmethod
    def method(self):
        pass

class ConcreteRepresentableClass(PureAbstractClass):
    __metaclass__ = AbstractRepresentable

    def __init__(self, a, b, c):
        super(ConcreteRepresentableClass, self).__init__(a, b)
        self.c = c

    def method(self):
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

    def test_field_requirement(self):
        try:
            WrongClass('a', 'b', 'c')
            self.fail("TypeError expected")
        except TypeError as te:
            self.assertTrue('missing_field' in str(te))

    def test_child_abstract_repr(self):
        # It's still abstract
        self.assertRaises(TypeError, AbstractClass, 5, 6)

        # But the concrete class is representable
        self.assertEquals(ConcreteClass(5,6,7), eval(repr(ConcreteClass(5,6,7))))
        self.assertNotEquals(ConcreteClass(6,5,7), eval(repr(ConcreteClass(5,6,7))))

    def test_child_pure_abstract_repr(self):
        self.assertEquals(ConcreteRepresentableClass(5,6,7), eval(repr(ConcreteRepresentableClass(5,6,7))))
        self.assertNotEquals(ConcreteRepresentableClass(6,5,7), eval(repr(ConcreteRepresentableClass(5,6,7))))

def suite():
    return unittest.makeSuite(RepresentableTestCase)

if __name__ == '__main__':
    unittest.main()

