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
import time

import weblab.experiment.experiment as Experiment
import weblab.core.coordinator.coordinator as Coordinator

from voodoo.override import Override

class DummyBatchExperiment(Experiment.Experiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(DummyBatchExperiment,self).__init__(*args, **kwargs)
        
    @Override(Experiment.Experiment)
    def do_get_api(self):
        return "2"
    

    @Override(Experiment.Experiment)
    def do_start_experiment(self, serialized_client_initial_data, serialized_server_initial_data):

        print "Experiment started", serialized_client_initial_data, serialized_server_initial_data

        client_initial_data = json.loads(serialized_client_initial_data)
        self.finish_earlier = False
        self.take_time_finishing = False

        if client_initial_data.get('long_finish',True):
            self.take_time_finishing = True

        if client_initial_data.get('batch', True):
            return json.dumps({ "initial_configuration" : "this will be batch", "batch" : True })
        elif client_initial_data.get('early_finish', True):
            self.finish_earlier = True
            self.original_time = time.time()
            return json.dumps({ "initial_configuration" : "this will not be batch, but it will finish in 10 seconds (earlier than expected)", "batch" : False })
        if client_initial_data.get('long_finish',True):
            return json.dumps({ "initial_configuration" : "this will not be batch, but it will take long to finish (10 seconds)", "batch" : False })

        return json.dumps({ "initial_configuration" : "Normal use...", "batch" : False })

    @Override(Experiment.Experiment)
    def do_dispose(self):
        if self.take_time_finishing:
            print "Disposing experiment..."
            time.sleep(10)
        return_value = json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : True, Coordinator.FINISH_DATA_MESSAGE : "This is the final data"})
        print "Experiment disposed. Returning", return_value
        return return_value

    @Override(Experiment.Experiment)
    def do_should_finish(self):
        print "should_finish called"
        if self.finish_earlier:
            remaining = (self.original_time + 10) - time.time()
            if remaining == 0:
                print "Should finish: -1"
                return -1
            print "Should finish:",remaining
            return remaining
        print "Should finish: 0"
        return 0

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

