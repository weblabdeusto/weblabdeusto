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

import weblab.experiment.Experiment as Experiment

from voodoo.override import Override

class JavaDummyExperiment(Experiment.Experiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(JavaDummyExperiment, self).__init__(*args, **kwargs)

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        print "Experiment started"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        print "Received command: %s" % command
        return "Received command: %s" % command

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        print "Received file with len: %s and file_info: %s" % (len(content), file_info)
        return "Received file with len: %s and file_info: %s" % (len(content), file_info)

    @Override(Experiment.Experiment)
    def do_dispose(self):
        print "dispose"

