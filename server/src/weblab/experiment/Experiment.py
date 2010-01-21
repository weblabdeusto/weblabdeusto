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
import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions

class Experiment(object):

    def __init__(self, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)

    def do_start_experiment(self):
        # Default implementation: empty
        pass

    def do_send_file_to_device(self, file_content, file_info):
        """do_send_file_to_device(file_content, file_info)
        raises (FeatureNotImplemented, SendingFileFailureException)
        """
        raise ExperimentExceptions.FeatureNotImplementedException(
                "send_file_to_device has not been implemented in this experiment"
            )

    def do_send_command_to_device(self, command):
        """do_send_command_to_device(command)
        raises (FeatureNotImplemented, SendingCommandFailureException)
        """
        raise ExperimentExceptions.FeatureNotImplementedException(
                "send_command_to_device has not been implemented in this experiment"
            )

    def do_dispose(self):
        # Default implementation: empty
        pass

