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

Experiment = [
        'start_experiment',
        'send_file_to_device',
        'send_command_to_device',
        'dispose'
    ]

Laboratory = [ 
        'reserve_experiment',
        'free_experiment',
        'send_file',
        'send_command',
        'resolve_experiment_address'
    ]

UserProcessing = [
        'reserve_session'
    ]
    
