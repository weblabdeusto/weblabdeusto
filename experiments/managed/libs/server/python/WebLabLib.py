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

##########################################################################
# 
# There are two ways of implementing an Experiment Server in
# Python:
# 
#  * Using the WebLab infrastructure (see weblab.experiment.experiments)
#   
#  * As standalone simple applications, as this one
# 
# The advantage of the first approach is that the developer has access
# to all the tools provided by voodoo, including the deployment tools.
# An experiment developed this way can be in the same process as the 
# Laboratory Server, or communicate in a faster way.
# 
# However, the second approach is far simpler for a programmer not 
# involved or new to the WebLab-Deusto project.
# 
# In order to use the second approach, you should make a class that
# inherits from ExperimentServer, and use Launcher to run it :-)
# 


class ExperimentServer(object):
    def start_experiment(self):
        pass

    def send_file(self, content, file_info):
        pass

    def send_command(self, command_string):
        pass

    def dispose(self):
        pass

import SimpleXMLRPCServer


