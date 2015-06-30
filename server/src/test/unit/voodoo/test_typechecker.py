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
import operator

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

@typecheck(typechecker.LIST(int))
def check_list_integer(elements):
    return reduce(operator.add, elements)

@typecheck(typechecker.TUPLE(float))
def check_tuple_float(elements):
    return reduce(operator.add, elements)

@typecheck(typechecker.ITERATION(float))
def check_iteration_float(elements):
    return reduce(operator.add, elements)


@typecheck('Point', 'Point')
def sum_points(point1, point2):
    return point1 + point2

class Point(object):
    @typecheck(int, int)
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @typecheck('Point')
    def __add__(self, other):
        return Point( self.x + other.x, self.y + other.y )

@typecheck('Point', 'Point', check_module = True)
def sum_two_points(point1, point2):
    return point1 + point2


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

    def test_list_int(self):
        result = check_list_integer([1, 2, 3])
        self.assertEquals(1 + 2 + 3, result)

        self.assertRaises(TypeError, check_list_integer, (1, 2, 3))
        self.assertRaises(TypeError, check_list_integer, [1, 2, 3.0])

    def test_tuple_float(self):
        result = check_tuple_float((1.0, 2.0, 3.0))
        self.assertEquals(1.0 + 2.0 + 3.0, result)

        self.assertRaises(TypeError, check_tuple_float, (1.0, 2.0, 3))
        self.assertRaises(TypeError, check_tuple_float, [1.0, 2.0, 3.0])

    def test_iteration_float(self):
        result = check_iteration_float((1.0, 2.0, 3.0))
        self.assertEquals(1.0 + 2.0 + 3.0, result)

        result = check_iteration_float([1.0, 2.0, 3.0])
        self.assertEquals(1.0 + 2.0 + 3.0, result)

        self.assertRaises(TypeError, check_iteration_float, (1.0, 2.0, 3))

    def test_none(self):
        self.assertEquals(10, sumnone(5,5))
        self.assertEquals("none", sumnone(5,None))

    def test_any(self):
        self.assertEquals(10, sumany(5,5))
        self.assertEquals("foo", sumany(5,"foo"))

    def test_using_str_in_class(self):
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        p3 = p1 + p2
        self.assertEquals(4, p3.x)
        self.assertEquals(6, p3.y)

        self.assertRaises(TypeError, p1.__add__, 5)

    def test_using_str_in_function(self):
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        p3 = sum_points(p1, p2)
        self.assertEquals(4, p3.x)
        self.assertEquals(6, p3.y)

        self.assertRaises(TypeError, sum_points, p1, 5)

        p3 = sum_two_points(p1, p2)
        self.assertEquals(4, p3.x)
        self.assertEquals(6, p3.y)

        self.assertRaises(TypeError, sum_points, p1, 5)

    def test_using_str_wrongly(self):
        def method_that_fails(check):
            @typecheck('this.does.not.exist', check_module = check)
            def function(arg):
                pass

        self.assertRaises(TypeError, method_that_fails, True)
        method_that_fails(False) # No problem


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

