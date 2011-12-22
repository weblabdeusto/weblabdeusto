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
from voodoo.typechecker import typecheck

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

def suite():
    return unittest.makeSuite(TypeCheckTest)

if __name__ == '__main__':
    unittest.main()

