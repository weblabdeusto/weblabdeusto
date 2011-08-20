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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#

from mock import patch
import unittest

from test.util.fakeobjects import fakeaddinfourl
import test.unit.configuration as configuration_module

from weblab.experiment.experiments.ud_pic_experiment.UdPicExperiment import UdPicExperiment
import weblab.experiment.Util as ExperimentUtil
import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.experiment.exc as ExperimentExceptions
import weblab.experiment.experiments.ud_pic_experiment.exc as UdPicExperimentExceptions


class UdPicExperimentTestCase(unittest.TestCase):

    def setUp(self):
        UdPicExperiment.DEFAULT_SLEEP_TIME = 0.01
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        self.experiment = UdPicExperiment(None, None, cfg_manager)

    @patch('urllib2.urlopen')
    def test_send_command(self, urlopen):
        urlopen.return_value = fakeaddinfourl()
        self.experiment.do_send_command_to_device('PULSE=0 1000')

    @patch('urllib2.urlopen')
    def test_send_commands_plural(self, urlopen):
        urlopen.return_value = fakeaddinfourl()
        self.experiment.do_send_command_to_device('PULSE=0 1000, PULSE=0 500')

    def test_send_command_invalid_command(self):
        self.assertRaises(
            UdPicExperimentExceptions.InvalidUdPicBoardCommandException,
            self.experiment.do_send_command_to_device,
            'PULSE.THAT.DOES.NOT.EXIST=0 1000'
        )

# TODO: The PIC actually returns an index.html web page, so this must be changed
#   def test_send_command_invalid_response(self):
#       self.urllib_mock.expects(
#               pmock.once()
#           ).urlopen(
#               pmock.eq('http://localhost:80/pic.cgi'),
#               pmock.eq('PULSE 0 1000')
#           ).will(
#               pmock.return_value(StringIO.StringIO('not ok'))
#           )
#       self.assertRaises(
#           UdPicExperimentExceptions.UdPicInvalidResponseException,
#           self.experiment.do_send_command_to_device,
#           "PULSE 0 1000"
#       )
#       self.urllib_mock.verify()

# XXX: this test was not being executed. WATCH OUT!
#   def test_send_file(self):
#       FILE_CONTENT = "whatever the file content is \xff\x00"
#       self.popen_mock.stdin  = pmock.Mock()
#       self.popen_mock.stdout = pmock.Mock()
#       self.popen_mock.stderr = pmock.Mock()
#       self.popen_mock.stdin.expects(
#               pmock.once()
#           ).method('write')
#       self.popen_mock.stdin.expects(
#               pmock.once()
#           ).close()
#       self.popen_mock.expects(
#               pmock.once()
#           ).wait().will(
#               pmock.return_value(0)
#           )
#       self.popen_mock.stdout.expects(
#               pmock.once()
#           ).read().will(
#               pmock.return_value("tftp> tftp> Sent 17 bytes in 0.0 seconds")
#           )
#
#       self.popen_mock.stderr.expects(
#               pmock.once()
#           ).read().will(
#               pmock.return_value("")
#           )
#
#       self.experiment.do_send_file_to_device(
#               ExperimentUtil.serialize(FILE_CONTENT)
#           )
#       self.popen_mock.stdin.verify()
#       self.popen_mock.stdout.verify()
#       self.popen_mock.stderr.verify()
#       self.popen_mock.verify()

    @patch('subprocess.Popen')
    @patch('urllib2.urlopen')
    def test_send_file(self, urlopen, Popen):
        urlopen.return_value = fakeaddinfourl()
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = 'tftp> tftp> tftp>'
        popen.stderr.read.return_value = ''

        self.experiment.do_send_file_to_device(
                ExperimentUtil.serialize(''),
                'program'
            )

    @patch('subprocess.Popen')
    @patch('urllib2.urlopen')
    def test_send_file_returns_nonzero(self, urlopen, Popen):
        urlopen.return_value = fakeaddinfourl()
        popen = Popen.return_value
        popen.wait.return_value = -1
        popen.stdout.read.return_value = 'tftp> tftp> Sent 17 bytes in 0.0 seconds'
        popen.stderr.read.return_value = ''

        self.assertRaises(
                ExperimentExceptions.SendingFileFailureException,
                self.experiment.do_send_file_to_device,
                ExperimentUtil.serialize('whatever the file content is \xff\x00'),
                'program'
            )

    @patch('subprocess.Popen')
    @patch('urllib2.urlopen')
    def test_send_file_not_sent_message(self, urlopen, Popen):
        urlopen.return_value = fakeaddinfourl()
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = 'this is not a sent message'
        popen.stderr.read.return_value = ''

        self.assertRaises(
                ExperimentExceptions.SendingFileFailureException,
                self.experiment.do_send_file_to_device,
                ExperimentUtil.serialize('whatever the file content is \xff\x00'),
                'program'
            )

    @patch('subprocess.Popen')
    @patch('urllib2.urlopen')
    def test_send_file_stderr_used(self, urlopen, Popen):
        urlopen.return_value = fakeaddinfourl()
        popen = Popen.return_value
        popen.wait.return_value = 0
        popen.stdout.read.return_value = 'tftp> tftp> Sent 17 bytes in 0.0 seconds'
        popen.stderr.read.return_value = 'some message in stderr'

        self.assertRaises(
                ExperimentExceptions.SendingFileFailureException,
                self.experiment.do_send_file_to_device,
                ExperimentUtil.serialize('whatever the file content is \xff\x00'),
                'program'
            )


def suite():
    return unittest.makeSuite(UdPicExperimentTestCase)

if __name__ == '__main__':
    unittest.main()
