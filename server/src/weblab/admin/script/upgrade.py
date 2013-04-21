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

import sys

from weblab.admin.cli.controller import DbConfiguration
from weblab.admin.script.utils import run_with_config

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
    def on_dir(directory, configuration_files):
        db_conf = DbConfiguration(configuration_files)
        regular_url = db_conf.build_url()
        coord_url   = db_conf.build_coord_url()
        upgrader = DbUpgrader(regular_url, coord_url)
        if not upgrader.check_updated():
            print "Upgrading database...",
            upgrader.upgrade()
            print "[done]"

    run_with_config(directory, on_dir)

