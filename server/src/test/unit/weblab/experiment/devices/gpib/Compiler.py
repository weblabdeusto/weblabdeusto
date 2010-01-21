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
import pmock

import test.unit.configuration as configuration_module

import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.experiment.devices.gpib.Gpib as Gpib
import weblab.exceptions.experiment.devices.gpib.GpibExceptions as GpibExceptions

import test.unit.weblab.experiment.devices.gpib.fake_compiler_linker_nice as fake_compiler_linker_nice

class WrappedCompiler(Gpib.Compiler):
    def _check(self, file_path):
        pass

class WrappedCompilerPopen(WrappedCompiler):
    def __init__(self, *args, **kargs):
        self.raise_exception = False
        self.mocked_popen    = pmock.Mock()
        WrappedCompiler.__init__(self, *args, **kargs)

    def _create_popen(self, cmd_file):
        if self.raise_exception:
            raise Exception("alehop")
        return self.mocked_popen

class FakeTimer(object):
    @staticmethod
    def sleep(time):
        pass # :-)

class GpibCompilerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

    def test_error_creating_popen(self):
        compiler = WrappedCompilerPopen(self.cfg_manager)
        compiler._time_module = FakeTimer
        compiler.raise_exception = True

        self.assertRaises(
            GpibExceptions.ErrorProgrammingDeviceException,
            compiler.compile_file,
            'whatever.exe'
        )

    def test_error_waiting(self):
        compiler = WrappedCompilerPopen(self.cfg_manager)
        compiler._time_module = FakeTimer
        compiler.mocked_popen.expects(
                pmock.once()
            ).method('poll').will(
                pmock.raise_exception(Exception("alehop"))
            )

        self.assertRaises(
            GpibExceptions.ErrorWaitingForProgrammingFinishedException,
            compiler.compile_file,
            'whatever.exe'
        )

    def test_error_reading(self):
        compiler = WrappedCompilerPopen(self.cfg_manager)
        compiler._time_module = FakeTimer
        compiler.mocked_popen.expects(
                pmock.once()
            ).method('poll').will(
                pmock.return_value(0)
            )

        compiler.mocked_popen.stdout = pmock.Mock()
        compiler.mocked_popen.stdout.expects(
                pmock.once()
            ).method('read').will(
                pmock.raise_exception(Exception('alehop'))
            )

        self.assertRaises(
            GpibExceptions.ErrorRetrievingOutputFromProgrammingProgramException,
            compiler.compile_file,
            'whatever.exe'
        )

    def test_compiler(self):
        compiler = WrappedCompiler(self.cfg_manager)
        compiler._time_module = FakeTimer

        gpib_compiler_command_property = 'gpib_compiler_command'
        gpib_linker_command_property = 'gpib_linker_command'

        # It works
        self.assertEquals(
            'whatever.exe',
            compiler.compile_file("whatever.cpp")
        )

        # Change to the bad compiler
        self.assertRaises(
            GpibExceptions.ProgrammingGotErrors,
            compiler.compile_file,
            "show error.cpp"
        )
        self.assertRaises(
            GpibExceptions.ProgrammingGotErrors,
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
            GpibExceptions.ProgrammingGotErrors,
            compiler.compile_file,
            "show error.cpp"
        )
        self.assertRaises(
            GpibExceptions.ProgrammingGotErrors,
            compiler.compile_file,
            "return -1.cpp"
        )

    def test_compiler_errors(self):
        compiler = WrappedCompiler(self.cfg_manager)
        compiler._time_module = FakeTimer

        self.cfg_manager._values['gpib_compiler_command'] = []

        self.assertRaises(
            GpibExceptions.InvalidGpibProperty,
            compiler.compile_file,
            "foo"
        )
        self.cfg_manager._values.pop('gpib_compiler_command')
                
        self.assertRaises(
            GpibExceptions.CantFindGpibProperty,
            compiler.compile_file,
            "bar"
        )
        self.cfg_manager.reload()

        compiler = WrappedCompiler(self.cfg_manager)

        self.cfg_manager._values['gpib_linker_command'] = []

        self.assertRaises(
            GpibExceptions.InvalidGpibProperty,
            compiler.compile_file,
            "foo"
        )
        self.cfg_manager._values.pop('gpib_linker_command')
                
        self.assertRaises(
            GpibExceptions.CantFindGpibProperty,
            compiler.compile_file,
            "bar"
        )

    def tearDown(self):
        self.cfg_manager.reload()

def suite():
    return unittest.makeSuite(GpibCompilerTestCase)

if __name__ == '__main__':
    unittest.main()

