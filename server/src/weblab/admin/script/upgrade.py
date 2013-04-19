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
from weblab.admin.script.utils import check_dir_exists

from weblab.db.upgrade import DbUpgrader

#########################################################################################
# 
# 
# 
#      W E B L A B     U P G R A D E
# 
# 
# 


def weblab_upgrade(directory):
    # TODO: this comes from weblab_admin
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


        # TODO: this comes from weblab.admin.cli.controller
        from weblab.admin.cli.controller import get_variable
        import weblab.configuration_doc as configuration_doc

        for configuration_file in configuration_files:
            if not os.path.exists(configuration_file):
                print >> sys.stderr, "Could not find configuration file", configuration_file
                sys.exit(1)

            globals()['CURRENT_PATH'] = configuration_file
            execfile(configuration_file, globals(), globals())

        global_vars = globals()

        db_host           = get_variable(global_vars, configuration_doc.DB_HOST)
        db_port           = get_variable(global_vars, configuration_doc.DB_PORT)
        db_engine         = get_variable(global_vars, configuration_doc.DB_ENGINE)
        db_name           = get_variable(global_vars, configuration_doc.DB_DATABASE)
        db_user           = get_variable(global_vars, configuration_doc.WEBLAB_DB_USERNAME)
        db_pass           = get_variable(global_vars, configuration_doc.WEBLAB_DB_PASSWORD)

        print db_host, db_port, db_engine, db_name, db_user, db_pass
        url = ""
        DbUpgrader(url)

    finally:
        os.chdir(old_cwd)

    print >> sys.stderr, "Upgrading is not yet implemented"
