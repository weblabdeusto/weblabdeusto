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

# This is the visible API of each server of the WebLab

Login = []

UserProcessing = [
        'reserve_session'
    ]

Proxy = [
        'enable_access',
        'disable_access',
        'are_expired',
        'retrieve_results'
    ]

Laboratory = [ 
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
    ]

Translator = [
        'on_start',
        'before_send_command',
        'after_send_command',
        'before_send_file',
        'after_send_file',
        'on_finish'
    ]

Experiment = [
        'start_experiment',
        'send_file_to_device',
        'send_command_to_device',
        'should_finish',
        'dispose',
        'is_up_and_running',
    ]

