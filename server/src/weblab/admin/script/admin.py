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

import os

from voodoo.gen.loader.ConfigurationParser import GlobalParser

from weblab.admin.cli.controller import Controller
from weblab.admin.script.utils import check_dir_exists

#########################################################################################
# 
# 
# 
#      W E B L A B     A D M I N
# 
# 
# 

def weblab_admin(directory):
    check_dir_exists(directory)
    old_cwd = os.getcwd()
    os.chdir(directory)
    try:
        parser = GlobalParser()
        global_configuration = parser.parse('.')
        configuration_files = []
        configuration_files.extend(global_configuration.configurations)
        for machine in global_configuration.machines:
            machine_config = global_configuration.machines[machine]
            configuration_files.extend(machine_config.configurations)

            for instance in machine_config.instances:
                instance_config = machine_config.instances[instance]
                configuration_files.extend(instance_config.configurations)

                for server in instance_config.servers:
                    server_config = instance_config.servers[server]
                    configuration_files.extend(server_config.configurations)

        Controller(configuration_files)
    finally:
        os.chdir(old_cwd)

