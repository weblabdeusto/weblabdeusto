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

    def do_start_experiment(self, client_initial_data, server_initial_data):
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

    def do_should_experiment_finish(self):
        # 
        # Should the experiment finish? If the experiment server should be able to
        # say "I've finished", it will be asked every few time; if the experiment
        # is completely interactive (so it's up to the user and the permissions of
        # the user to say when the session should finish), it will never be asked.
        # 
        # Therefore, this method will return a numeric result, being:
        #   - result > 0: it hasn't finished but ask within result seconds.
        #   - result == 0: completely interactive, don't ask again
        #   - result == -1: it has finished.
        # 
        return 0

    def do_dispose(self):
        # 
        # Default implementation: no, I haven't finished cleaning resources
        # 
        return False

    def do_are_resources_clean(self):
        # 
        # If dispose() returned "True" (i.e. it's still cleaning resources),
        # it will keep calling this method until the resources are cleaned.
        # Until this happens, the system will consider that the experiment
        # can't be assigned to other student.
        # 
        # It will be a numeric + string value where the numeric value is:
        #  - result > 0: It has not finished, and this is a stimation of how
        #                long will it take. For instance, it can return that
        #                it will take 3 seconds if it does not know how long
        #                it will take.
        #  - result == 0: It has finished.
        #  - result == -1: There was an error.
        # 
        # The string value is the (result, string)
        # 
        return (0, '')
        

    def do_is_up_and_running(self):
        # 
        # Is the experiment up and running?
        # 
        # The scheduling system will ensure that the experiment will not be
        # assigned to other student while this method is called. The result
        # is an array of integer + String, where the first argument is:
        # 
        #   - result >= 0: "the experiment is OK; please check again 
        #                  within $result seconds"
        #   - result == 0: the experiment is OK and I can't perform a proper
        #                  estimation
        #   - result == -1: "the experiment is broken"
        # 
        # And the second (String) argument is the message detailing while 
        # it failed
        # 
        return (600, '') # Default value: check every 10 minutes

