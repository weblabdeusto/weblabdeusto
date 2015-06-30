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
# 
from __future__ import print_function, unicode_literals
import unittest

import datetime

from voodoo.gen import CoordAddress
from weblab.core.new_server import simplify_response

class SimplifyResponseTestCase(unittest.TestCase):

    def test_simplify_response_str(self):
        self._check("hello","hello")

    def test_simplify_response_unicode(self):
        self._check(u"hello",u"hello")

    def test_simplify_response_number(self):
        self._check(5,5)

    def test_simplify_response_simplelist(self):
        simplelist = [5,6,"foo"]
        self._check(simplelist, simplelist)

    def test_simplify_response_simpletuple(self):
        simplelist = (5,6,"foo")
        self._check(simplelist, list(simplelist))

    def test_simplify_response_simpledict(self):
        simpledict = { "a" : "b", 5 : "foo", u"bar" : 5 }
        self._check(simpledict, simpledict)

    def test_simplify_response_datetime_datetime(self):
        dt = datetime.datetime(2009, 7, 19, 9, 39)
        expected = '2009-07-19T09:39:00'
        self._check(dt, expected)

    def test_simplify_response_datetime_date(self):
        dt = datetime.date(2009, 7, 19)
        expected = '2009-07-19'
        self._check(dt, expected)

    def test_simplify_response_datetime_time(self):
        dt = datetime.time(9, 39)
        expected = '09:39:00'
        self._check(dt, expected)

    def test_simplify_response_oldclass(self):
        class A:
            def __init__(self):
                self.attr1 = "foo"
                self.attr2 = "bar"

            def method(self):
                pass

        a = A()
        self._check(a, {"attr1" : "foo", "attr2" : "bar"})

    def test_simplify_response_newclass(self):
        class A(object):
            def __init__(self):
                super(A, self).__init__()
                self.attr1 = "foo"
                self.attr2 = "bar"

            def method(self):
                pass

        a = A()
        self._check(a, {"attr1" : "foo", "attr2" : "bar"})

    def test_simplify_response_coordaddr(self):
        addr = CoordAddress('mach','inst','serv')
        self._check(addr, {'process': 'inst', 'component': 'serv', 'host': 'mach'})

    def test_simplify_response_maxdepth(self):
        class A(object):
            def __init__(self):
                super(A, self).__init__()
                self.attr1 = "foo"

            def method(self):
                pass

        a = A()
        a.a = a
        self._check(a, {
                "attr1" : "foo", 
                "a" : {
                    "attr1" : "foo",
                    "a" : {
                        "attr1" : None,
                        "a" : None
                    }
                }
            }, limit = 3)

    def _check(self, msg, expected, limit = None):
        if limit is not None:
            simplified = simplify_response(msg, limit = limit)
        else:
            simplified = simplify_response(msg)
        self.assertEquals(simplified, expected)


def suite():
    return unittest.makeSuite(SimplifyResponseTestCase)

if __name__ == '__main__':
    unittest.main()

