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
import mocker

import test.unit.configuration as configuration_module

import voodoo.configuration as ConfigurationManager

import weblab.experiment.devices.gpib.gpib as Gpib
import weblab.experiment.devices.gpib.exc as GpibErrors

import test.unit.weblab.experiment.devices.gpib.fake_compiler_linker_nice as fake_compiler_linker_nice


class FakeTimer(object):
    @staticmethod
    def sleep(time):
        pass # :-)

class WrappedCompiler(Gpib.Compiler):

    _time = FakeTimer

    _fail_in_create_popen = False

    def __init__(self, popen_mock, *args, **kargs):
        super(WrappedCompiler, self).__init__(*args, **kargs)
        self._popen_mock = popen_mock

    def _create_popen(self, cmd_file):
        if self._fail_in_create_popen:
            raise Exception("alehop")
        # We accept both a mock or using real popen in tests
        if self._popen_mock is None:
            return super(WrappedCompiler, self)._create_popen(cmd_file)
        else:
            return self._popen_mock

    def _check(self, file_path):
        pass

    def _log(self, action, result_code, output, stderr):
        pass

class GpibCompilerTestCase(mocker.MockerTestCase):

    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

    def test_error_creating_popen(self):
        compiler = WrappedCompiler(None, self.cfg_manager)
        compiler._fail_in_create_popen = True

        self.assertRaises(
            GpibErrors.ErrorProgrammingDeviceError,
            compiler.compile_file,
            'whatever.exe'
        )

        self.mocker.restore()

    def test_error_waiting(self):
        compiler = WrappedCompiler(self.mocker.mock(), self.cfg_manager)
        compiler._popen_mock.poll()
        self.mocker.throw(Exception("alehop"))

        self.mocker.replay()
        self.assertRaises(
            GpibErrors.ErrorWaitingForProgrammingFinishedError,
            compiler.compile_file,
            'whatever.exe'
        )

    def test_error_reading(self):
        compiler = WrappedCompiler(self.mocker.mock(), self.cfg_manager)
        compiler._popen_mock.poll()
        self.mocker.result(0)
        compiler._popen_mock.stdout.read()
        self.mocker.throw(Exception('alehop'))

        self.mocker.replay()
        self.assertRaises(
            GpibErrors.ErrorRetrievingOutputFromProgrammingProgramError,
            compiler.compile_file,
            'whatever.exe'
        )

    def test_compiler(self):
        gpib_compiler_command_property = 'gpib_compiler_command'
        gpib_linker_command_property = 'gpib_linker_command'

        compiler = WrappedCompiler(None, self.cfg_manager)

        # It works
        self.assertEquals(
            'whatever.exe',
            compiler.compile_file("whatever.cpp")
        )

        # Change to the bad compiler
        self.assertRaises(
            GpibErrors.ProgrammingGotErrors,
            compiler.compile_file,
            "show error.cpp"
        )
        self.assertRaises(
            GpibErrors.ProgrammingGotErrors,
            compiler.compile_file,
            "return -1.cpp"
        )

        # Change to a nice command
        self.cfg_manager._values[gpib_compiler_command_property] = ['python',fake_compiler_linker_nice.__file__.replace('.pyc','.py'), Gpib.CPP_FILE]

        fake_linker_command = self.cfg_manager._values[gpib_linker_command_property]
        self.cfg_manager._values[gpib_linker_command_property] = ['python',fake_compiler_linker_nice.__file__.replace('.pyc','.py'), Gpib.OBJ_FILE, Gpib.EXE_FILE]

        # Everything is fine
        self.assertEquals(
            'whatever.exe',
            compiler.compile_file("whatever.cpp")
        )
        self.assertEquals(
            'show error.exe',
            compiler.compile_file("show error.cpp")
        )
        self.assertEquals(
            'show stderr.exe',
            compiler.compile_file("show stderr.cpp")
        )
        self.assertEquals(
            'return -1.exe',
            compiler.compile_file("return -1.cpp")
        )

        # Now change to the bad linker
        self.cfg_manager._values[gpib_linker_command_property] = fake_linker_command
        # This one works
        self.assertEquals(
            'whatever.exe',
            compiler.compile_file("whatever.cpp")
        )

        # The others don't
        self.assertRaises(
            GpibErrors.ProgrammingGotErrors,
            compiler.compile_file,
            "show error.cpp"
        )
        self.assertRaises(
            GpibErrors.ProgrammingGotErrors,
            compiler.compile_file,
            "return -1.cpp"
        )

    def test_compiler_errors(self):
        compiler = WrappedCompiler(None, self.cfg_manager)

        self.cfg_manager._values['gpib_compiler_command'] = []

        self.assertRaises(
            GpibErrors.InvalidGpibProperty,
            compiler.compile_file,
            "foo"
        )
        self.cfg_manager._values.pop('gpib_compiler_command')

        self.assertRaises(
            GpibErrors.CantFindGpibProperty,
            compiler.compile_file,
            "bar"
        )
        self.cfg_manager.reload()

        compiler = WrappedCompiler(None, self.cfg_manager)

        self.cfg_manager._values['gpib_linker_command'] = []

        self.assertRaises(
            GpibErrors.InvalidGpibProperty,
            compiler.compile_file,
            "foo"
        )
        self.cfg_manager._values.pop('gpib_linker_command')

        self.assertRaises(
            GpibErrors.CantFindGpibProperty,
            compiler.compile_file,
            "bar"
        )

    def tearDown(self):
        self.cfg_manager.reload()

def suite():
    return unittest.makeSuite(GpibCompilerTestCase)

if __name__ == '__main__':
    unittest.main()

