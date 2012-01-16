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

import unittest

import voodoo.typechecker as typechecker
from voodoo.typechecker import typecheck, typecheckprop

class Calculator(object):

    @typecheck(int, int)
    def sum(self, arg1, arg2):
        return arg1 + arg2

    @typecheck(int, (int, float))
    def minus(self, arg1, arg2):
        return arg1 - arg2

@typecheck(int, int)
def sum(arg1, arg2):
    return arg1 + arg2

@typecheck(int, (int, typecheck.NONE))
def sumnone(arg1, arg2):
    if arg2 is None:
        return "none"
    return arg1 + arg2

@typecheck(int, typecheck.ANY)
def sumany(arg1, arg2):
    if arg2 == "foo":
        return "foo"
    return arg1 + arg2

@typecheck(int, basestring, basestring)
def sumdefaults(arg1, arg2 = 'foo', arg3 = 'bar'):
    return str(arg1) + arg2 + arg3

class PropertiesClass(object):
    @typecheck(int, int)
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    @typecheckprop(int)
    def x(self, value):
        self._x = value

class TypeCheckTest(unittest.TestCase):

    def test_normal(self):
        calc = Calculator()
        result = calc.sum(1,2)
        self.assertEquals(3, result)

        result = calc.minus(1,2)
        self.assertEquals(-1, result)

        result = calc.minus(1,2.5)
        self.assertEquals(-1.5, result)

        result = sum(3,4)
        self.assertEquals(7, result)

    def test_none(self):
        self.assertEquals(10, sumnone(5,5))
        self.assertEquals("none", sumnone(5,None))

    def test_any(self):
        self.assertEquals(10, sumany(5,5))
        self.assertEquals("foo", sumany(5,"foo"))
    
    def test_properties(self):
        point = PropertiesClass(5,6)
        self.assertEquals(5, point.x)
        point.x = 10
        self.assertEquals(10, point.x)
        def setter():
            point.x = "foo"
        self.assertRaises(TypeError, setter)

    def test_keywords(self):
        calc = Calculator()

        result = calc.sum(1,arg2=2)
        self.assertEquals(3, result)

        result = calc.sum(arg1=3,arg2=4)
        self.assertEquals(7, result)

        result = sum(5,arg2=6)
        self.assertEquals(11, result)

        result = sum(arg1=7,arg2=8)
        self.assertEquals(15, result)

    def test_failing(self):
        calc = Calculator()
        self.assertRaises(TypeError, calc.sum, '1', 2)
        self.assertRaises(TypeError, calc.sum, 1, '2')
        self.assertRaises(TypeError, calc.minus, 1, '2')
        self.assertRaises(TypeError, calc.sum, 1)
        self.assertRaises(TypeError, calc.sum, 1, 2, 3)
        self.assertRaises(TypeError, calc.sum, 1, arg3=2)
        self.assertRaises(TypeError, calc.sum, 1, arg1=2)

        self.assertRaises(TypeError, sum, '1', 2)
        self.assertRaises(TypeError, sum, 1, '2')
        self.assertRaises(TypeError, sum, 1)
        self.assertRaises(TypeError, sum, 1, 2, 3)
        self.assertRaises(TypeError, sum, 1, arg3=2)
        self.assertRaises(TypeError, sum, 1, arg1=2)

    def test_checking(self):
        typechecker.CHECKING = False
        try:
            calc = Calculator()
            calc.sum('1','2')
        finally:
            typechecker.CHECKING = True

    def test_defaults(self):
        self.assertRaises(TypeError, sumdefaults)
        self.assertEquals('1foobar', sumdefaults(1))
        self.assertEquals('1barbar', sumdefaults(1, 'bar'))
        self.assertEquals('1barfoo', sumdefaults(1, 'bar', 'foo'))
        self.assertRaises(TypeError, sumdefaults, 1, 'bar', 'foo', 'foobar')

def suite():
    return unittest.makeSuite(TypeCheckTest)

if __name__ == '__main__':
    unittest.main()

