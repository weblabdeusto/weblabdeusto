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

import tempfile
import os

import weblab.exceptions.experiment.experiments.ud_pic_experiment.UdPicExperimentExceptions as UdPicExperimentExceptions

class TFtpProgramSender(object):
    
    def __init__(self, tftp_device, tftp_remote_filename):
        super(TFtpProgramSender, self).__init__()
        self._tftp_device = tftp_device
        self._tftp_remote_filename =  tftp_remote_filename

    def send_content(self, file_content):
        fd, file_name = tempfile.mkstemp(
                prefix='ud_pic_experiment_program',suffix='.hex'
            )
        try:
            try:
                os.write(fd, file_content)
            finally:
                os.close(fd)
            
            result, stdout_result, stderr_result = self._tftp_device.put(
                    "put %s %s" % (file_name,self._tftp_remote_filename)
                )
            if result != 0:
                raise UdPicExperimentExceptions.UdPicInvalidResponseException("tftp returned %s" % result)
            if stdout_result.lower().find('tftp> tftp> sent') != 0 and stdout_result.lower().find('tftp> tftp> tftp>') != 0:
                raise UdPicExperimentExceptions.UdPicInvalidResponseException("Expected stdout: 'tftp> tftp> Sent' or 'tftp> tftp> tftp>'; found '%s'" % stdout_result)
            if len(stderr_result) > 0:
                raise UdPicExperimentExceptions.UdPicInvalidResponseException("Expected stderr: ''; found '%s'" % stderr_result)
        finally:
            os.remove(file_name)

