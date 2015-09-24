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
import weblab.experiment.exc as ExperimentErrors

import weblab.experiment.level as ExperimentApiLevel


import weblab.core.coordinator.coordinator as Coordinator
import json

class Experiment(object):

    def __init__(self, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)

    def do_start_experiment(self, client_initial_data, server_initial_data):
        """ do_start_experiment(client_initial_data, server_initial_data) -> initial_configuration

        This method indicates that a student has been assigned to use this
        laboratory. client_initial_data will provide the data (typically a
        JSON-serialized string) that the experiment client submitted (if any),
        and server_initial_data is a JSON-serialized string with the data passed
        by the core server. This includes the time slot available for the
        current user, the priority, etc.

        This method must return a JSON-serialized string which can be an empty
        object ("{}"), but it can state that it is a batch experiment (and
        therefore the scheduler will mark it as free once the start method has
        finished), and it can provide information that the client will receive
        (such as "the URL for the camera in this copy of the laboratory is this
        one").
        """
        # Default implementation: empty
        return "{}"

    def do_get_api(self):
        """
        do_get_api() -> api_version

        Reports the api version that the experiment uses. The default api level is the
        current one. Experiments may override this method to return a different one.

        TODO: Providing such a default might lead to errors, because if a new api was released
        old experiments which didn't override get_api would without warning be using a wrong api.
        It might be safer to enforce get_api() overriding, or to at least issue some kind of
        warning if an experiment doesn't.
        """
        return ExperimentApiLevel.current

    def do_send_file_to_device(self, file_content, file_info):
        """do_send_file_to_device(file_content, file_info)
        raises (FeatureNotImplemented, SendingFileFailureError)
        """
        raise ExperimentErrors.FeatureNotImplementedError(
                "send_file_to_device has not been implemented in this experiment"
            )

    def do_send_command_to_device(self, command):
        """do_send_command_to_device(command)
        raises (FeatureNotImplemented, SendingCommandFailureError)
        """
        raise ExperimentErrors.FeatureNotImplementedError(
                "send_command_to_device has not been implemented in this experiment"
            )

    def do_should_finish(self):
        """
        Should the experiment finish? If the experiment server should be able to
        say "I've finished", it will be asked every few time; if the experiment
        is completely interactive (so it's up to the user and the permissions of
        the user to say when the session should finish), it will never be asked.

        Therefore, this method will return a numeric result, being:
          - result > 0: it hasn't finished but ask within result seconds.
          - result == 0: completely interactive, don't ask again
          - result < 0: it has finished.
        """
        return 0

    def do_dispose(self):
        """
        Experiment should clean the resources now, and optionally return data. Default implementation: yes, I have finished.
        """
        return json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : True, Coordinator.FINISH_DATA_MESSAGE : ""})

    def do_is_up_and_running(self):
        """
        Is the experiment up and running?

        The scheduling system will ensure that the experiment will not be
        assigned to other student while this method is called. The result
        is an array of integer + String, where the first argument is:

          - result >= 0: "the experiment is OK; please check again
                         within $result seconds"
          - result == 0: the experiment is OK and I can't perform a proper
                         estimation
          - result == -1: "the experiment is broken"

        And the second (String) argument is the message detailing while
        it failed
        """
        return (600, '') # Default value: check every 10 minutes

