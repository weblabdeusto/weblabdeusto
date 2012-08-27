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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#

import weblab.admin.bot.cfg_util as cfg_util

HOST                = "localhost"                       # WebLab's hostname
USERNAME            = "student1"                        # WebLab's username to login
PASSWORD            = "password"                        # WebLab user's password do login
EXPERIMENT_NAME     = "ud-dummy"                        # Experiment name to interact with
CATEGORY_NAME       = "Dummy experiments"               # Experiment category name to interact with
PROGRAM_FILE        = "this is the content of the file" # Program file to send

ITERATIONS          = 10                                # Times to repeat each launch


GENERATE_GRAPHICS   = True
MATPLOTLIB_BACKEND  = 'cairo.pdf'
STEP_DELAY          = 0.05

SYSTEMS = {
            "blood"         : "Intel(R) Core(TM)2 Duo CPU T7250@2.00GHz reduced to 1.60 GHz; 3.5 GB RAM",
            "nctrun-laptop" : "Intel(R) Pentium(R) 4 CPU 3.40GHz with Hyperthreading (2); 2.0 GB RAM",
            "hook"          : "Intel(R) Pentium(R) 4 CPU 2.8GHz; 1.0 GB RAM",
            "ord3p"         : "Intel(R) Core(TM)2 Duo CPU T7250  @ 2.00GHz; 3.5 GB RAM",
            "skull"         : "Intel(R) Core(TM)2 Duo CPU E8400  @ 3.00GHz; 3.0 GB RAM",
            "lrg-ubuntu"    : "Intel(R) Xeon(R) CPU E5502  @ 1.87GHz; 4.0 GB RAM"
        }
SYSTEM = cfg_util.retrieve_system(SYSTEMS)

new_standard_bot_user = cfg_util.generate_new_standard_bot_user('http://%s' % HOST, USERNAME, PASSWORD, EXPERIMENT_NAME, CATEGORY_NAME, PROGRAM_FILE)

REVISION = cfg_util.generate_revision()

def generate_scenarios():
    Scenario = cfg_util.create_new_scenario()

    scenarios = []
    for protocol in cfg_util.get_supported_protocols():
        for number in range(1, 5):
            scenarios.append(
                    Scenario(
                        cfg_util.new_bot_users(number, new_standard_bot_user, 0, STEP_DELAY, protocol),
                        protocol, number
                    )
                )
        for number in range(5, 151, 5):
            scenarios.append(
                    Scenario(
                        cfg_util.new_bot_users(number, new_standard_bot_user, STEP_DELAY * (5 -1), STEP_DELAY, protocol),
                        protocol, number
                    )
                )
    return scenarios

CONFIGURATIONS      = [
                        "../../server/launch/sample/launch_sample.py",
#                        "../../server/launch/sample_xmlrpc/launch_sample_xmlrpc_machine.py",
#                        "../../server/launch/sample_internetsocket/launch_sample_internetsocket_machine.py",
#                        "../../server/launch/sample_unixsocket/launch_sample_unixsocket_machine.py",
#                        "../../server/launch/sample_balanced1/launch_sample_balanced1_machine.py",
                        "../../server/launch/sample_balanced2/launch_sample_balanced2_machine.py",
                        "../../server/launch/sample_balanced2_concurrent_experiments/launch_sample_balanced2_concurrent_experiments_machine.py",
                      ]

RUNNING_CONFIGURATION = "revision %s. %s iterations; step_delay: %s seconds;" % (REVISION, ITERATIONS, STEP_DELAY)

