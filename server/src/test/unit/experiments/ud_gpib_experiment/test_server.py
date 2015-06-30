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
import tempfile
import os

import test.unit.configuration as configuration_module

import experiments.ud_gpib.server as UdGpibExperiment
import weblab.experiment.util as ExperimentUtil
import voodoo.configuration as ConfigurationManager

import weblab.experiment.exc as ExperimentErrors
import experiments.ud_gpib.exc as GpibErrors

class FakeCompiler(object):
    def __init__(self):
        super(FakeCompiler,self).__init__()
        self.file_paths    = []
        self.files_content = []
        self.next_content  = ''
        self.fail_on_next  = False
        self.files_created = []

    def compile_file(self, file_path):
        if self.fail_on_next:
            raise Exception("Any given exception")
        self.file_paths.append(file_path)
        self.files_content.append(
                open(file_path).read()
            )
        fd, file_name = tempfile.mkstemp(dir='.')
        self.files_created.append(file_name)
        os.write(fd, self.next_content)
        os.close(fd)
        return file_name

class FakeLauncher(object):
    def __init__(self):
        super(FakeLauncher,self).__init__()
        self.file_paths    = []
        self.files_content = []
        self.next_content  = ''
        self.fail_on_next  = False

    def execute(self, file_path, background):
        if self.fail_on_next:
            raise Exception("Any given exception")
        self.file_paths.append(file_path)
        self.files_content.append(open(file_path).read())
        f = open('output.txt','w')
        f.write(self.next_content)
        f.close()
        return 0,'stdout result','stderr result'

    def poll(self):
        return self.poll_ok

    def get_result_code(self):
        return self.result_code

    def get_result_stdout(self):
        return self.result_stdout

    def get_result_stderr(self):
        return self.result_stderr

class WrappedUdGpibExperiment(UdGpibExperiment.UdGpibExperiment):

    def __init__(self, coord_address, locator, cfg_manager, compiler, launcher):
        self.__compiler = compiler
        self.__launcher = launcher
        super(WrappedUdGpibExperiment, self).__init__(coord_address, locator, cfg_manager)

    def _create_gpib_compiler(self, cfg_manager):
        return self.__compiler

    def _create_gpib_launcher(self, cfg_manager):
        return self.__launcher

    def _read_output_file(self):
        if self.read_ok:
            return self.output_file_content
        else:
            raise Exception("error!")

class UdGpibExperimentTestCase(unittest.TestCase):

    def setUp(self):
        self.compiler = FakeCompiler()
        self.launcher = FakeLauncher()

        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.experiment = WrappedUdGpibExperiment(
                None,
                None,
                self.cfg_manager,
                self.compiler,
                self.launcher
            )

    def tearDown(self):
        for file_created in self.compiler.files_created:
            try:
                os.remove(file_created)
            except:
                pass

        try:
            os.remove('output.txt')
        except:
            pass

    def test_send_file(self):
        CPP_FILE_CONTENT = """Content of the cpp file"""
        EXE_FILE_CONTENT = """Content of the exe file"""

        self.compiler.next_content = EXE_FILE_CONTENT

        self.experiment.do_send_file_to_device(
                ExperimentUtil.serialize(CPP_FILE_CONTENT),
                'program'
            )
        self.experiment.do_dispose()

        # Check the compiler
        self.assertEquals(
                1,
                len(self.compiler.file_paths)
            )
        self.assertFalse( os.path.exists(
                self.compiler.file_paths[0]
            ))
        self.assertEquals(
                1,
                len(self.compiler.files_content)
            )
        self.assertEquals(
                CPP_FILE_CONTENT,
                self.compiler.files_content[0]
            )

        # Check the launcher
        self.assertEquals(
                1,
                len(self.launcher.file_paths)
            )
#       self.assertFalse( os.path.exists(
#               self.launcher.file_paths[0]
#           ))
        self.assertEquals(
                1,
                len(self.launcher.files_content)
            )
        self.assertEquals(
                EXE_FILE_CONTENT,
                self.launcher.files_content[0]
            )

    def test_send_command_to_device_poll_ok(self):
        self.launcher.poll_ok = True
        response = self.experiment.do_send_command_to_device("POLL")
        self.assertEquals("OK", response)

    def test_send_command_to_device_poll_wait(self):
        self.launcher.poll_ok = False
        response = self.experiment.do_send_command_to_device("POLL")
        self.assertEquals("WAIT", response)

    def test_send_command_to_device_result_code(self):
        self.launcher.result_code = 0
        response = self.experiment.do_send_command_to_device("RESULT code")
        self.assertEquals(0, response)

    def test_send_command_to_device_result_stdout(self):
        self.launcher.result_stdout = "Weblab rulez!"
        response = self.experiment.do_send_command_to_device("RESULT stdout")
        self.assertEquals("Weblab rulez!", response)

    def test_send_command_to_device_result_stderr(self):
        self.launcher.result_stderr = "Error!"
        response = self.experiment.do_send_command_to_device("RESULT stderr")
        self.assertEquals("Error!", response)

    def test_send_command_to_device_result_file_ok(self):
        FILE_CONTENT = "This is my output file!"
        self.experiment.read_ok = True
        self.experiment.output_file_content = FILE_CONTENT
        response = self.experiment.do_send_command_to_device("RESULT file")
        self.assertEquals("OK" + FILE_CONTENT, response)

    def test_send_command_to_device_result_file_error(self):
        self.experiment.read_ok = False
        self.experiment.output_file_content = "This is my output file!"
        response = self.experiment.do_send_command_to_device("RESULT file")
        self.assertEqual("ER", response[0:2])

    def test_send_command_to_device_unknown_command(self):
        self.assertRaises(
            GpibErrors.UnknownUdGpibCommandError,
            self.experiment.do_send_command_to_device,
            "ThisIsNotAValidCommand!"
        )

    def test_failures(self):
        CPP_FILE_CONTENT = """Content of the cpp file"""
        self.compiler.fail_on_next = True
        self.assertRaises(
            ExperimentErrors.SendingFileFailureError,
            self.experiment.do_send_file_to_device,
            ExperimentUtil.serialize(CPP_FILE_CONTENT),
            'program'
        )
        self.experiment.do_dispose()

def suite():
    return unittest.makeSuite(UdGpibExperimentTestCase)

if __name__ == '__main__':
    unittest.main()

