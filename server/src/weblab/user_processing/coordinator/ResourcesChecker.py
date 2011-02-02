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

import traceback

import voodoo.LogLevel as LogLevel
import voodoo.log as log
import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.data.ServerType as ServerType

class ResourcesChecker(object):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.locator     = coordinator.locator

    def check(self):
        experiments_per_laboratory = self.coordinator.list_laboratories_addresses()
        for laboratory_address_str in experiments_per_laboratory:
            self.check_laboratory(laboratory_address_str, experiments_per_laboratory[laboratory_address_str])

    def check_laboratory(self, address_str, experiments):
        try:
            address = CoordAddress.CoordAddress.translate_address(address_str)
            server = self.locator.get_server_from_coordaddr(address, ServerType.Laboratory)
            failing_experiments = server.check_experiments_resources()
            for failing_experiment in failing_experiments:
                if not failing_experiment in experiments:
                    log.log( ResourcesChecker, LogLevel.Error,
                            "Laboratory server %s reported that experiment %s was failing; however this laboratory does NOT manage this experiment. Attack?" % (address_str, failing_experiment))
                    continue

                self.coordinator.mark_experiment_as_broken(failing_experiment, failing_experiments[failing_experiment])

            for experiment in experiments:
                if not experiment in failing_experiments:
                    # Experiment works!
                    self.coordinator.mark_experiment_as_fixed(experiment)
            
        except:
            traceback.print_exc()
            log.log( ResourcesChecker, LogLevel.Critical,
                    "Error checking resources of laboratory %s " % address_str)
            log.log_exc(ResourcesChecker, LogLevel.Critical)

