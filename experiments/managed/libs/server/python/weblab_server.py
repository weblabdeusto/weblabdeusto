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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

"""
There are two ways of implementing an Experiment Server in
Python:
 
 * Using the WebLab infrastructure (see weblab.experiment.experiments)
  
 * As standalone simple applications, as this one
 
The advantage of the first approach is that the developer has access
to all the tools provided by voodoo, including the deployment tools.
An experiment developed this way can be in the same process as the 
Laboratory Server, or communicate in a faster way.

However, the second approach is far simpler for a programmer not 
involved or new to the WebLab-Deusto project.
 
In order to use the second approach, you should make a class that
inherits from ExperimentServer, and use the launch method to run it :-)
""" 

import traceback
import SimpleXMLRPCServer

class ExperimentServer(object):

    def test_me(self, message):
        return message

    def is_up_and_running(self):
        return True
    
    def start_experiment(self, client_initial_data, server_initial_data):
        return "{}"

    def send_file(self, content, file_info):
        return "ok"

    def send_command(self, command_string):
        return "ok"

    def dispose(self):
        return "{}"

    def should_finish(self):
        return 0

    def get_api(self):
        return "2"
    

class WebLabHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    rpc_paths = '/','/RPC2','/weblab/xmlrpc','/weblab/xmlrpc/','/weblab','/weblab/'

class XMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    def _dispatch(self, *args, **kwargs):
        try:
            return SimpleXMLRPCServer.SimpleXMLRPCServer._dispatch(self, *args, **kwargs)
        except:
            traceback.print_exc()
            raise
    
class Launcher(object):
    
    def __init__(self, port, experiment_server):
        super(Launcher, self).__init__()
        self.port = port
        self.experiment_server = experiment_server

    def start(self):
        self.server = XMLRPCServer(("", self.port), WebLabHandler)
        self.server.register_function(self.experiment_server.test_me, "Util.test_me")
        self.server.register_function(self.experiment_server.is_up_and_running, "Util.is_up_and_running")
        self.server.register_function(self.experiment_server.start_experiment, "Util.start_experiment")
        self.server.register_function(self.experiment_server.send_file, "Util.send_file_to_device")
        self.server.register_function(self.experiment_server.send_command, "Util.send_command_to_device")
        self.server.register_function(self.experiment_server.dispose, "Util.dispose")
        self.server.register_function(self.experiment_server.get_api, "Util.get_api")
        self.server.register_function(self.experiment_server.should_finish, "Util.should_finish")
        print "Running XML-RPC server on port %i" % self.port
        self.server.serve_forever()
