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

from __future__ import with_statement

import unittest
import StringIO
from mocker import Mocker

import test.unit.configuration as configuration_module

import weblab.experiment.experiments.ud_pic_experiment.UdPicExperiment as UdPicExperiment
import weblab.experiment.Util as ExperimentUtil
import weblab.experiment.devices.http_device.HttpDevice as HttpDevice
import weblab.experiment.devices.tftp_device.TFtpDevice as TFtpDevice
import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions
import weblab.exceptions.experiment.experiments.ud_pic_experiment.UdPicExperimentExceptions as UdPicExperimentExceptions

import FakeTempfile

HTTP_SERVER_HOSTNAME = "localhost"
HTTP_SERVER_PORT     = 80
HTTP_SERVER_APP      = "pic.cgi"
TFTP_SERVER_HOSTNAME = "localhost"
TFTP_SERVER_PORT     = 69
TFTP_SERVER_FILENAME = "sample_filename"


class WrappedUdPicExperiment(UdPicExperiment.UdPicExperiment):

    def __init__(self, coord_address, locator, cfg_manager, tftp, http):
        self.__tftp = tftp
        self.__http = http
        super(WrappedUdPicExperiment, self).__init__(coord_address, locator, cfg_manager)
        self._tftp_program_sender._tempfile = FakeTempfile
        
    def _create_tftp_device(self, hostname, port):
        assert hostname == TFTP_SERVER_HOSTNAME
        assert port     == TFTP_SERVER_PORT
        return self.__tftp
    
    def _create_http_device(self, hostname, port, app):
        assert hostname == HTTP_SERVER_HOSTNAME
        assert port     == HTTP_SERVER_PORT
        assert app      == HTTP_SERVER_APP
        return self.__http

class WrappedHttpDevice(HttpDevice.HttpDevice):
    
    def __init__(self, urlmodule, *args, **kargs):
        super(WrappedHttpDevice,self).__init__(*args, **kargs)
        self.__urlmodule = urlmodule
        
    def _urlmodule(self):
        return self.__urlmodule

class WrappedTFtpDevice(TFtpDevice.TFtpDevice):
    
    def __init__(self, popen, *args, **kargs):
        super(WrappedTFtpDevice, self).__init__(*args, **kargs)
        self.__popen = popen
        
    def _create_popen(self, cmd_file):
        assert cmd_file == ['tftp',TFTP_SERVER_HOSTNAME, str(TFTP_SERVER_PORT)]
        return self.__popen

class UdPicExperimentTestCase(unittest.TestCase):
    
    def setUp(self):
        self.mocker = Mocker()
        self.urllib_mock = self.mocker.mock()
        self.popen_mock  = self.mocker.mock()

        self.http = WrappedHttpDevice(self.urllib_mock,
                    HTTP_SERVER_HOSTNAME,
                    HTTP_SERVER_PORT,
                    HTTP_SERVER_APP
                )
        self.tftp = WrappedTFtpDevice(self.popen_mock,
                    TFTP_SERVER_HOSTNAME,
                    TFTP_SERVER_PORT
                )

        self.cfg_manager= ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)
        
        UdPicExperiment.DEFAULT_SLEEP_TIME = 0.01

        self.experiment = WrappedUdPicExperiment(
                None,
                None,
                self.cfg_manager,
                self.tftp,
                self.http
            )

    def test_send_command(self):
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'PULSE=0 1000')
        self.mocker.result(StringIO.StringIO('ok'))
        
        with self.mocker:
            self.experiment.do_send_command_to_device("PULSE=0 1000")

    def test_send_commands_plural(self):
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'PULSE=0 1000')
        self.mocker.result(StringIO.StringIO('ok'))
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'PULSE=0 500')
        self.mocker.result(StringIO.StringIO('ok'))
        
        with self.mocker:
            self.experiment.do_send_command_to_device("PULSE=0 1000, PULSE=0 500")

    def test_send_command_invalid_command(self):
        with self.mocker:
            self.assertRaises(
                UdPicExperimentExceptions.InvalidUdPicBoardCommandException,
                self.experiment.do_send_command_to_device,
                "PULSE.THAT.DOES.NOT.EXIST=0 1000"
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

    def test_send_file(self):
        FILE_CONTENT = ""
        self.popen_mock.stdin.write('binary\nput /tmp/ud_pic_experiment_programT3MP0R4L.hex sample_filename\n')
        self.popen_mock.stdin.close()
        self.popen_mock.wait()
        self.mocker.result(0)
        self.popen_mock.stdout.read()
        self.mocker.result("tftp> tftp> tftp>")
        self.popen_mock.stderr.read()
        self.mocker.result("")
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'RESET=')
        self.mocker.result(StringIO.StringIO('ok'))

        with self.mocker:
            self.experiment.do_send_file_to_device(
                    ExperimentUtil.serialize(FILE_CONTENT),
                    'program'
                )

    def test_send_file_returns_nonzero(self):
        FILE_CONTENT = "whatever the file content is \xff\x00"
        self.popen_mock.stdin.write('binary\nput /tmp/ud_pic_experiment_programT3MP0R4L.hex sample_filename\n')
        self.popen_mock.stdin.close()
        self.popen_mock.wait()
        self.mocker.result(-1) # There was an error!
        self.popen_mock.stdout.read()
        self.mocker.result("tftp> tftp> Sent 17 bytes in 0.0 seconds")
        self.popen_mock.stderr.read()
        self.mocker.result("")
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'RESET=')
        self.mocker.result(StringIO.StringIO('ok'))

        with self.mocker:
            self.assertRaises(
                    ExperimentExceptions.SendingFileFailureException,
                    self.experiment.do_send_file_to_device,
                    ExperimentUtil.serialize(FILE_CONTENT),
                    'program'
                )

    def test_send_file_not_sent_message(self):
        FILE_CONTENT = "whatever the file content is \xff\x00"
        self.popen_mock.stdin.write('binary\nput /tmp/ud_pic_experiment_programT3MP0R4L.hex sample_filename\n')
        self.popen_mock.stdin.close()
        self.popen_mock.wait()
        self.mocker.result(0)
        self.popen_mock.stdout.read()
        self.mocker.result("this is not a sent message") # Message not expected
        self.popen_mock.stderr.read()
        self.mocker.result("")
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'RESET=')
        self.mocker.result(StringIO.StringIO('ok'))

        with self.mocker:
            self.assertRaises(
                    ExperimentExceptions.SendingFileFailureException,
                    
                    self.experiment.do_send_file_to_device,
                    ExperimentUtil.serialize(FILE_CONTENT),
                    'program'
                )

    def test_send_file_stderr_used(self):
        FILE_CONTENT = "whatever the file content is \xff\x00"
        self.popen_mock.stdin.write('binary\nput /tmp/ud_pic_experiment_programT3MP0R4L.hex sample_filename\n')
        self.popen_mock.stdin.close()
        self.popen_mock.wait()
        self.mocker.result(0)
        self.popen_mock.stdout.read()
        self.mocker.result("tftp> tftp> Sent 17 bytes in 0.0 seconds")
        self.popen_mock.stderr.read()
        self.mocker.result("some message in stderr") # stderr used
        self.urllib_mock.urlopen('http://localhost:80/pic.cgi', 'RESET=')
        self.mocker.result(StringIO.StringIO('ok'))
        
        with self.mocker:
            self.assertRaises(
                    ExperimentExceptions.SendingFileFailureException,
                    
                    self.experiment.do_send_file_to_device,
                    ExperimentUtil.serialize(FILE_CONTENT),
                    'program'
                )


def suite():
    return unittest.makeSuite(UdPicExperimentTestCase)

if __name__ == '__main__':
    unittest.main()

