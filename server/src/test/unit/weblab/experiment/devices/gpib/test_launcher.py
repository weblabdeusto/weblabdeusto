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

class WrappedLauncherPopen(Gpib.Launcher):

    _fail_in_create_popen = False

    def __init__(self, popen_mock, *args, **kargs):
        self.raise_exception = False
        self._popen_mock = popen_mock
        Gpib.Launcher.__init__(self, *args, **kargs)

    def _create_popen(self, cmd_file):
        if self._fail_in_create_popen:
            raise Exception("alehop")
        return self._popen_mock


class GpibLauncherTestCase(mocker.MockerTestCase):

    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

    def test_error_creating_popen_not_background(self):
        launcher = WrappedLauncherPopen(self.mocker.mock(), self.cfg_manager)
        launcher._fail_in_create_popen = True

        self.mocker.replay()
        self.assertRaises(
            GpibErrors.ErrorProgrammingDeviceError,
            launcher.execute,
            'whatever.exe',
            False
        )

    def test_error_creating_popen_background(self):
        launcher = WrappedLauncherPopen(self.mocker.mock(), self.cfg_manager)
        launcher._fail_in_create_popen = True

        self.mocker.replay()
        self.assertRaises(
            GpibErrors.ErrorProgrammingDeviceError,
            launcher.execute,
            'whatever.exe',
            True
        )

    def test_error_waiting_not_background(self):
        launcher = WrappedLauncherPopen(self.mocker.mock(), self.cfg_manager)
        launcher._popen_mock.poll()
        self.mocker.throw(Exception("alehop"))

        self.mocker.replay()
        self.assertRaises(
            GpibErrors.ErrorWaitingForProgrammingFinishedError,
            launcher.execute,
            'whatever.exe',
            False
        )

    def test_error_waiting_background(self):
        launcher = WrappedLauncherPopen(self.mocker.mock(), self.cfg_manager)
        launcher._popen_mock.poll()
        self.mocker.throw(Exception("alehop"))

        self.mocker.replay()
        result_execute = launcher.execute("whatever.exe", True)
        self.assertEquals(None, result_execute)

        self.assertRaises(
            GpibErrors.ErrorWaitingForProgrammingFinishedError,
            launcher.poll
        )

    def test_error_reading_not_background(self):
        launcher = WrappedLauncherPopen(self.mocker.mock(), self.cfg_manager)
        launcher._popen_mock.poll()
        self.mocker.result(0)
        launcher._popen_mock.stdout.read()
        self.mocker.throw(Exception('alehop'))

        self.mocker.replay()
        self.assertRaises(
            GpibErrors.ErrorRetrievingOutputFromProgrammingProgramError,
            launcher.execute,
            'whatever.exe',
            False
        )

    def test_error_reading_background(self):
        launcher = WrappedLauncherPopen(self.mocker.mock(), self.cfg_manager)
        launcher._popen_mock.poll()
        self.mocker.result(0)
        launcher._popen_mock.stdout.read()
        self.mocker.throw(Exception('alehop'))

        self.mocker.replay()
        result_execute = launcher.execute("whatever.exe", True)
        self.assertEquals(None, result_execute)

        self.assertRaises(
            GpibErrors.ErrorRetrievingOutputFromProgrammingProgramError,
            launcher.poll
        )

    def tearDown(self):
        self.cfg_manager.reload()

def suite():
    return unittest.makeSuite(GpibLauncherTestCase)

if __name__ == '__main__':
    unittest.main()