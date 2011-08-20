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

import json

import weblab.experiment.Experiment as Experiment

from voodoo.override import Override

class DummyBatchExperiment(Experiment.Experiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(DummyBatchExperiment,self).__init__(*args, **kwargs)

    @Override(Experiment.Experiment)
    def do_dispose(self):
        print "Experiment disposed"
        return ""

    @Override(Experiment.Experiment)
    def do_start_experiment(self, *args, **kwargs):
        print "Experiment started", args, kwargs
        return json.dumps({ "initial_configuration" : "hi, from dummy batch experiment", "batch" : True })

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        msg = "Received command: %s" % command
        print msg
        return msg

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        msg = "Received file with len: %s and file_info: %s" % (len(content), file_info)
        print msg
        return msg

