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
import sys

from voodoo.gen.loader.ConfigurationParser import GlobalParser

def check_dir_exists(directory, parser = None):
    if not os.path.exists(directory):
        if parser is not None:
            parser.error("ERROR: Directory %s does not exist" % directory)
        else:
            print >> sys.stderr, "ERROR: Directory %s does not exist" % directory
        sys.exit(-1)
    if not os.path.isdir(directory):
        if parser is not None:
            parser.error("ERROR: File %s exists, but it is not a directory" % directory)
        else:
            print >> sys.stderr, "ERROR: Directory %s does not exist" % directory
        sys.exit(-1)


def run_with_config(directory, func):
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
        return func(directory, configuration_files)
    finally:
        os.chdir(old_cwd)

