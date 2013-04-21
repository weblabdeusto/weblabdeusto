#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

from weblab.admin.cli.controller import Controller
from weblab.admin.script.utils import run_with_config

#########################################################################################
# 
# 
# 
#      W E B L A B     A D M I N
# 
# 
# 

def weblab_admin(directory):
    def on_dir(directory, configuration_files):
        Controller(configuration_files)
    
    run_with_config(directory, on_dir)
