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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import unittest

from weblab.admin.cli.console_ui import ConsoleUI, GO_BACK_KEYWORD
from weblab.admin.cli.exc import GoBackException

class ConsoleUITestCase(unittest.TestCase):

    def setUp(self):
        self.ui = MockedConsoleUI()

    #
    # _format_label()
    #

    def test_format_label_not_nullable_and_not_default(self):
        label = self.ui._format_label("Name", nullable=False, default=None)
        self.assertEquals(label, "Name: ")

    def test_format_label_not_nullable_and_default(self):
        label = self.ui._format_label("Name", nullable=False, default="Jaime")
        self.assertEquals(label, "Name [default: Jaime]: ")

    def test_format_label_nullable_and_not_default(self):
        label = self.ui._format_label("Name", nullable=True, default=None)
        self.assertEquals(label, "Name [default: <null>]: ")

    def test_format_label_nullable_and_default(self):
        self.assertRaises(AssertionError,
                          self.ui._format_label,
                          "Name", nullable=True, default="Jaime")

    #
    # _in_range()
    #

    def test_in_range_ok(self):
        inrange = self.ui._in_range(5, 4, 6)
        self.assertTrue(inrange)

    def test_in_range_too_low(self):
        inrange = self.ui._in_range(3, 4, 6)
        self.assertFalse(inrange)

    def test_in_range_too_high(self):
        inrange = self.ui._in_range(7, 4, 6)
        self.assertFalse(inrange)

    #
    # _valid_list_of_emails()
    #

    def test_valid_list_of_emails_ok(self):
        valid = self.ui._valid_list_of_emails(["a@a.com", "b@b.com"])
        self.assertTrue(valid)

    def test_valid_list_of_emails_at_missing(self):
        valid = self.ui._valid_list_of_emails(["a@a.com", "bb.com"])
        self.assertFalse(valid)

    def test_valid_list_of_emails_dot_missing(self):
        valid = self.ui._valid_list_of_emails(["a@a.com", "b@bcom"])
        self.assertFalse(valid)

    #
    # _csv_to_tuple()
    #

    def test_csv_to_tuple_ok(self):
        tuple_resulted = self.ui._csv_to_tuple("a, b")
        self.assertEquals(tuple_resulted, ("a", "b"))

    def test_csv_to_tuple_none(self):
        tuple_resulted = self.ui._csv_to_tuple(None)
        self.assertEquals(tuple_resulted, ())

    #
    # _read_int()
    #

    def test_read_int_ok(self):
        self.ui._raw_input_buffer = "5"
        number = self.ui._read_int("Number", default=None)
        self.assertEquals(number, 5)

    def test_read_int_default(self):
        self.ui._raw_input_buffer = ""
        number = self.ui._read_int("Number", default=5)
        self.assertEquals(number, 5)

    def test_read_int_back(self):
        self.ui._raw_input_buffer = GO_BACK_KEYWORD
        self.assertRaises(GoBackException,
                          self.ui._read_int,
                          "Number", default=None)

    #
    # _read_str()
    #

    def test_read_str_ok(self):
        self.ui._raw_input_buffer = "Jaime"
        text = self.ui._read_str("Name", default=None)
        self.assertEquals(text, "Jaime")

    def test_read_str_default(self):
        self.ui._raw_input_buffer = ""
        text = self.ui._read_str("Name", default="Jaime")
        self.assertEquals(text, "Jaime")

    def test_read_str_back(self):
        self.ui._raw_input_buffer = GO_BACK_KEYWORD
        self.assertRaises(GoBackException,
                          self.ui._read_str,
                          "Name", default=None)

    #
    # _read_password()
    #

    def test_read_password_ok(self):
        self.ui._getpass_buffer = "password"
        password = self.ui._read_password("Password", default=None)
        self.assertEquals(password, "password")

    def test_read_password_default(self):
        self.ui._getpass_buffer = ""
        password = self.ui._read_password("Password", default="password")
        self.assertEquals(password, "password")

    def test_read_password_back(self):
        self.ui._getpass_buffer = GO_BACK_KEYWORD
        self.assertRaises(GoBackException,
                          self.ui._read_password,
                          "Password", default=None)

    #
    # _read_field_int()
    #

    def test_read_field_int_nullable_ok(self):
        self.ui._raw_input_buffer = "5"
        number = self.ui._read_field_int("Number", nullable=True)
        self.assertEquals(number, 5)

    def test_read_field_int_nullable_empty(self):
        self.ui._raw_input_buffer = ""
        number = self.ui._read_field_int("Number", nullable=True)
        self.assertEquals(number, None)

    def test_read_field_int_not_nullable_ok(self):
        self.ui._raw_input_buffer = "5"
        number = self.ui._read_field_int("Number", nullable=False)
        self.assertEquals(number, 5)

    #
    # _read_field_int_from_list()
    #

    def test_read_field_int_from_list_ok(self):
        self.ui._raw_input_buffer = "0"
        option = self.ui._read_field_int_from_list("Option", [0,2,3])
        self.assertEquals(option, 0)

    # this case should also be tested
    #def test_read_field_int_from_list_not_in_list(self):

    #
    # _read_field_str()
    #

    def test_read_field_str_nullable_ok(self):
        self.ui._raw_input_buffer = "Jaime"
        text = self.ui._read_field_str("Name", nullable=True)
        self.assertEquals(text, "Jaime")

    def test_read_field_str_nullable_empty(self):
        self.ui._raw_input_buffer = ""
        text = self.ui._read_field_str("Name", nullable=True)
        self.assertEquals(text, None)

    def test_read_field_str_not_nullable_ok(self):
        self.ui._raw_input_buffer = "Jaime"
        text = self.ui._read_field_str("Name", nullable=False)
        self.assertEquals(text, "Jaime")

    # this case should also be tested
    #def test_read_field_str_not_nullable_empty(self):

    #
    # _read_field_choose()
    #

    def test_read_field_choose_ok(self):
        self.ui._raw_input_buffer = "0"
        option = self.ui._read_field_choose("Option", [(0,"red"), (2,"green"), (3,"blue")])
        self.assertEquals(option, 0)

    def test_read_field_choose_no_options_and_not_nullable(self):
        self.assertRaises(AssertionError,
                          self.ui._read_field_choose,
                          "Option", [], nullable=False)





class MockedConsoleUI(ConsoleUI):

    def __init__(self):
        super(MockedConsoleUI, self).__init__()
        self._raw_input_buffer = ""
        self._getpass_buffer = ""
        self._stdout_buffer = ""

    def _raw_input(self, prompt):
        return self._raw_input_buffer

    def _getpass(self, prompt):
        return self._getpass_buffer

    def _print(self, text=""):
        self._stdout_buffer += text


def suite():
    return unittest.makeSuite(ConsoleUITestCase)

if __name__ == '__main__':
    unittest.main()
