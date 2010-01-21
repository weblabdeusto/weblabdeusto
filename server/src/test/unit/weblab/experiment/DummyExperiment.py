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

class DummyExperiment(Experiment.Experiment):
    def __init__(self, *args, **kwargs):
        super(DummyExperiment,self).__init__(*args, **kwargs)

    def do_send_file_to_device(self, *args, **kargs):
        pass
    
    def do_send_command_to_device(self, *args, **kargs):
        pass

