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

import six
import unittest
import threading
import thread
import pickle
import datetime
import xmlrpclib
import urllib2
import xml.parsers.expat as expat_parser

import voodoo.mapper as mapper

class MyClass(object):
    def __init__(self,first_field,second_field,third_field):
        object.__init__(self)
        self._first_field = first_field
        self._second_field = second_field
        self._third_field = third_field
        self.sum_of_fields = first_field + second_field
        self.another = threading.Lock()
        self.yet_another = 5.5
    def my_method(self):
        self.another.acquire()
        self.another.release()

class MyOtherClass:
    def __init__(self,param):
        self.param = param
        self.param2 = open(__file__)

class JetAnotherClass:
    def __init__(self,param):
        self.otherReference = param

class MyClass2(object):
    pass

class MyError(Exception): pass

class SimpleClass: pass

class MapperTestCase(unittest.TestCase):
    def test_dto_generator(self):
        mc = MyClass(1,2,(1,2))
        mc.and_another = MyClass(1,3,(1,3))

        moc = MyOtherClass(4+4j)

        # Cyclic references
        jac1 = JetAnotherClass(None)
        jac2 = JetAnotherClass(jac1)
        jac1.otherReference = jac2

        # mc and moc can't be pickled
        # pickle raises pickle.PicklingError in Python < 2.7 but TypeError in Python 2.7; we try both exceptions
        try:
            self.assertRaises(
                   pickle.PicklingError,
                   pickle.dumps,
                   mc
               )
        except:
            first_assertion_failed = True
        else:
            first_assertion_failed = False

        try:
            self.assertRaises(
                   TypeError,
                   pickle.dumps,
                   mc
               )
        except:
            if first_assertion_failed:
               raise

        self.assertRaises(
                TypeError,
                pickle.dumps,
                moc
            )

        my_dto = mapper.dto_generator(mc)

        self.assertEquals(
                my_dto._first_field,
                mc._first_field
            )
        self.assertEquals(
                my_dto._second_field,
                mc._second_field
            )
        self.assertEquals(
                my_dto._third_field,
                mc._third_field
            )
        self.assertEquals(
                my_dto.sum_of_fields,
                mc.sum_of_fields
            )
        self.assertNotEquals( #Lock not allowed
                type(my_dto.another),
                thread.LockType
            )
        self.assertEquals(
                my_dto.yet_another,
                mc.yet_another
            )
        # And inside and_another... so on
        self.assertEquals(
                my_dto.and_another._first_field,
                mc.and_another._first_field
            )

        # What about moc?
        my_other_dto = mapper.dto_generator(moc)
        self.assertEquals(
                my_other_dto.param,
                moc.param
            )
        self.assertEquals(
                hasattr(my_other_dto,'param2'),
                False
            )

        # What about JetAnotherClass?
        my_other_jac1 = mapper.dto_generator(jac1)
        my_other_jac1.otherReference


        # Go ahead! Pickle me! ;-D
        pickled     = pickle.dumps(my_dto)
        my_dto2     = pickle.loads(pickled)

        pickled     = pickle.dumps(my_other_dto)
        my_other_dto2   = pickle.loads(pickled)

        # Let's try to unload them
        my_dto2 = mapper.load_from_dto(my_dto2)

        my_other_dto2 = mapper.load_from_dto(my_other_dto2)

        # Let's check locks work
        my_dto2.my_method() #Nothing happens :-)

    def test_mapping_ignorable(self):
        native_obj = expat_parser.ParserCreate()
        self.assertRaises(
                    pickle.PicklingError,
                    pickle.dumps,
                    native_obj
            )

        class MyClass(object):
            pass

        my_class = MyClass()
        my_class.native_obj = native_obj

        dto = mapper.dto_generator(my_class)
        my_class2 = mapper.load_from_dto(dto)
        self.assertTrue(isinstance(my_class2.native_obj,six.string_types))

    def test_dto_not_comparable_instances(self):
        dt = xmlrpclib.DateTime()
        # DateTime throws exception when doing:
        #   dt == {}
        # for instance
        dto = mapper.dto_generator({"foo" : dt})
        dt2 = mapper.load_from_dto(dto)
        self.assertEquals(["foo"], dt2.keys())
        self.assertEquals(dt.value, dt2["foo"].value)

    def test_dto_exception(self):
        exception = MyError("foo")
        dto = mapper.dto_generator(exception)
        generated = mapper.load_from_dto(dto)
        self.assertTrue(isinstance(generated,MyError))
        self.assertEquals("foo", generated.args[0] )

    def test_dto_builtin(self):
        exception = AttributeError("foo")
        dto = mapper.dto_generator(exception)
        generated = mapper.load_from_dto(dto)
        self.assertTrue(isinstance(generated,AttributeError))
        self.assertEquals("foo", generated.args[0] )

    def test_dto_datetime(self):
        sc = SimpleClass()
        sc.time = datetime.datetime(2007, 12, 31, 23, 55)
        dto = mapper.dto_generator(sc)
        sc2 = mapper.load_from_dto(dto)
        self.assertEquals(2007, sc2.time.year)
        self.assertEquals(12  , sc2.time.month)
        self.assertEquals(31  , sc2.time.day)
        self.assertEquals(23  , sc2.time.hour)
        self.assertEquals(55  , sc2.time.minute)

    def test_skip_recoverables(self):
        a = SimpleClass()
        a.l = threading.Lock()

        dto = mapper.dto_generator(a)
        a2  = mapper.load_from_dto(dto, skip_recoverables = True)
        self.assertEquals(None, a2.l)
        a3  = mapper.load_from_dto(dto, skip_recoverables = False)
        self.assertTrue(isinstance(a3.l, thread.LockType))

    def test_remove_unpickables_lock(self):
        a = SimpleClass()
        a.l = threading.Lock()

        mapper.remove_unpickables(a)

        self.assertEquals(None, a.l)

    def test_remove_unpickables_not_comparable_instances(self):
        dt = xmlrpclib.DateTime()
        # DateTime throws exception when doing:
        #   dt == {}
        # for instance
        mapper.remove_unpickables({"foo" : dt})

    def test_remove_unpickables_datetime(self):
        sc = SimpleClass()
        sc.time = datetime.datetime(2007, 12, 31, 23, 55)
        mapper.remove_unpickables(sc)
        self.assertEquals(2007, sc.time.year)
        self.assertEquals(12  , sc.time.month)
        self.assertEquals(31  , sc.time.day)
        self.assertEquals(23  , sc.time.hour)
        self.assertEquals(55  , sc.time.minute)

    def test_remove_unpickables_ignorable(self):
        parser = expat_parser.ParserCreate()
        self.assertRaises(
                    pickle.PicklingError,
                    pickle.dumps,
                    parser
            )

        my_class = MyClass2()
        my_class.parser = parser

        mapper.remove_unpickables(my_class)

        pickle.dumps(my_class) # No problem now
        self.assertEqual(None, my_class.parser)

    def test_remove_unpickables_general(self):
        mc = MyClass(1,2,(1,2))
        mc.and_another = MyClass(1,3,(1,3))

        moc = MyOtherClass(4+4j)

        # Cyclic references
        jac1 = JetAnotherClass(None)
        jac2 = JetAnotherClass(jac1)
        jac1.otherReference = jac2

        # mc and moc can't be pickled
        # pickle raises pickle.PicklingError in Python < 2.7 but TypeError in Python 2.7; we try both exceptions
        try:
            self.assertRaises(
                pickle.PicklingError,
                pickle.dumps,
                mc
            )
        except:
            failed_first_time = True
        else:
            failed_first_time = False

        try:
            self.assertRaises(
                TypeError,
                pickle.dumps,
                mc
            )
        except:
            if failed_first_time:
               raise


        self.assertRaises(
                TypeError,
                pickle.dumps,
                moc
            )

        mapper.remove_unpickables(mc)

        self.assertEquals(
                1,
                mc._first_field
            )
        self.assertEquals(
                2,
                mc._second_field
            )
        self.assertEquals(
                (1,2),
                mc._third_field
            )
        self.assertEquals(
                1 + 2,
                mc.sum_of_fields
            )
        self.assertEquals( #Lock not allowed
                None,
                mc.another
            )
        self.assertEquals(
                5.5,
                mc.yet_another
            )
        # And inside and_another... so on
        self.assertEquals(
                1,
                mc.and_another._first_field
            )

        # What about moc?
        mapper.remove_unpickables(moc)
        self.assertEquals(
                4+4j,
                moc.param
            )
        self.assertEquals(
                None,
                moc.param2
            )

        # What about JetAnotherClass?
        mapper.remove_unpickables(jac1)

        # Go ahead! Pickle me! ;-D
        pickled      = pickle.dumps(mc)
        pickle.loads(pickled)

        pickled      = pickle.dumps(moc)
        pickle.loads(pickled)

    def test_remove_unpickables_http_exception(self):
        try:
            urllib2.urlopen("http://localhost/this.does.not.exist")
            self.fail("exception expected")
        except urllib2.URLError as e:
            pass
        except urllib2.HTTPError as e:
            pass

        removed = mapper.remove_unpickables(e)
        pickled = pickle.dumps(removed)
        pickle.loads(pickled)

    def test_condition(self):
        c1 = threading.Condition()
        dto = mapper.dto_generator(c1)
        c2 = mapper.load_from_dto(dto)
        self.assertTrue(hasattr(c2, 'acquire'))
        self.assertTrue(hasattr(c2, 'release'))

def suite():
    return unittest.makeSuite(MapperTestCase)

if __name__ == '__main__':
    unittest.main()

