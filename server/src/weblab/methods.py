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

# This is the visible API of each server of the WebLab

core = []

laboratory = [
        'reserve_experiment',
        'free_experiment',
        'send_file',
        'send_async_file',
        'send_command',
        'send_async_command',
        'check_async_command_status',
        'resolve_experiment_address',
        'check_experiments_resources',
        'experiment_is_up_and_running',
        'should_experiment_finish',
        'list_experiments',
    ]

experiment = [
        'start_experiment',
        'send_file_to_device',
        'send_command_to_device',
        'should_finish',
        'dispose',
        'is_up_and_running',
        'get_api'
    ]


Proxy = [
        'enable_access',
        'disable_access',
        'are_expired',
        'retrieve_results'
    ]


Translator = [
        'on_start',
        'before_send_command',
        'after_send_command',
        'before_send_file',
        'after_send_file',
        'on_finish'
    ]



UserProcessing = core # Compatibility with older versions
Experiment = experiment
Laboratory = laboratory

