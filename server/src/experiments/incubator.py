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

import json
import uuid
import hashlib
import datetime

import weblab.experiment.concurrent_experiment as ConcurrentExperiment
import weblab.core.coordinator.coordinator as Coordinator

from voodoo.override import Override



class IncubatorExperiment(ConcurrentExperiment.ConcurrentExperiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(IncubatorExperiment,self).__init__(*args, **kwargs)

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_get_api(self):
        return "2_concurrent"

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_start_experiment(self, lab_session_id, serialized_client_initial_data, serialized_server_initial_data):
        return json.dumps({ "initial_configuration" : "", "batch" : False })

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_dispose(self, lab_session_id):
        return 'ok'

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_send_command_to_device(self, lab_session_id, command):
        return 'Not implemented'

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_send_file_to_device(self, lab_session_id, content, file_info):
        return 'Not implemented'

