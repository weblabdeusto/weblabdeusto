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

class WrappedLauncherPopen(Gpib.Launcher):
    
    def __init__(self, *args, **kargs):
        self.raise_exception = False
        self.mocked_popen    = pmock.Mock()
        Gpib.Launcher.__init__(self, *args, **kargs)

    def _create_popen(self, cmd_file):
        if self.raise_exception:
            raise Exception("alehop")
        return self.mocked_popen
    
class GpibLauncherTestCase(unittest.TestCase):
    
    def setUp(self):
        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        
    def test_error_creating_popen_not_background(self):
        launcher = WrappedLauncherPopen(self.cfg_manager)
        launcher.raise_exception = True

        self.assertRaises(
            GpibExceptions.ErrorProgrammingDeviceException,
            launcher.execute,
            'whatever.exe',
            False
        )

    def test_error_creating_popen_background(self):
        launcher = WrappedLauncherPopen(self.cfg_manager)
        launcher.raise_exception = True

        self.assertRaises(
            GpibExceptions.ErrorProgrammingDeviceException,
            launcher.execute,
            'whatever.exe',
            True
        )

    def test_error_waiting_not_background(self):
        launcher = WrappedLauncherPopen(self.cfg_manager)
        launcher.mocked_popen.expects(
                pmock.once()
            ).method('poll').will(
                pmock.raise_exception(Exception("alehop"))
            )

        self.assertRaises(
            GpibExceptions.ErrorWaitingForProgrammingFinishedException,
            launcher.execute,
            'whatever.exe',
            False
        )

    def test_error_waiting_background(self):
        launcher = WrappedLauncherPopen(self.cfg_manager)
        launcher.mocked_popen.expects(
                pmock.once()
            ).method('poll').will(
                pmock.raise_exception(Exception("alehop"))
            )

        result_execute = launcher.execute("whatever.exe", True)
        self.assertEquals(None, result_execute)

        self.assertRaises(
            GpibExceptions.ErrorWaitingForProgrammingFinishedException,
            launcher.poll
        )

    def test_error_reading_not_background(self):
        launcher = WrappedLauncherPopen(self.cfg_manager)
        launcher.mocked_popen.expects(
                pmock.once()
            ).method('poll').will(
                pmock.return_value(0)
            )

        launcher.mocked_popen.stdout = pmock.Mock()
        launcher.mocked_popen.stdout.expects(
                pmock.once()
            ).method('read').will(
                pmock.raise_exception(Exception('alehop'))
            )

        self.assertRaises(
            GpibExceptions.ErrorRetrievingOutputFromProgrammingProgramException,
            launcher.execute,
            'whatever.exe',
            False
        )
        
    def test_error_reading_background(self):
        launcher = WrappedLauncherPopen(self.cfg_manager)
        launcher.mocked_popen.expects(
                pmock.once()
            ).method('poll').will(
                pmock.return_value(0)
            )

        launcher.mocked_popen.stdout = pmock.Mock()
        launcher.mocked_popen.stdout.expects(
                pmock.once()
            ).method('read').will(
                pmock.raise_exception(Exception('alehop'))
            )
            
        result_execute = launcher.execute("whatever.exe", True)
        self.assertEquals(None, result_execute)

        self.assertRaises(
            GpibExceptions.ErrorRetrievingOutputFromProgrammingProgramException,
            launcher.poll
        )

    def tearDown(self):
        self.cfg_manager.reload()

def suite():
    return unittest.makeSuite(GpibLauncherTestCase)

if __name__ == '__main__':
    unittest.main()
