#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#

import json
import argparse
from weblab_server import ExperimentServer, Launcher


class DummyExperimentServer(ExperimentServer):
    
    def start_experiment(self, client_initial_data, server_initial_data):
        print "start_experiment", client_initial_data, server_initial_data
        return "{}"

    def get_api(self):
        return "2"
        
    def send_file(self, content, file_info):
        print "send_file", file_info
        return "ok"
        
    def send_command(self, command_string):
        print "send_command", command_string
        return command_string
    
    def dispose(self):
        print "dispose"
        return "{}"

    def should_finish(self):
        return 0
    
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument("-p", "--port", type=int, default=12345,
                        help="port to listen")
    args = parser.parse_args()

    launcher = Launcher(args.port, DummyExperimentServer())
    launcher.start()
