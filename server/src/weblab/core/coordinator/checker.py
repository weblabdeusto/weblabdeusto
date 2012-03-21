#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005 onwards University of Deusto
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

import voodoo.log as log
import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.data.server_type as ServerType

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
            broken_resources = {}
            address = CoordAddress.CoordAddress.translate_address(address_str)
            server = self.locator.get_server_from_coordaddr(address, ServerType.Laboratory)
            failing_experiments = server.check_experiments_resources()
            for failing_experiment in failing_experiments:
                if not failing_experiment in experiments:
                    log.log( ResourcesChecker, log.level.Error,
                            "Laboratory server %s reported that experiment %s was failing; however this laboratory does NOT manage this experiment. Attack?" % (address_str, failing_experiment))
                    continue

                broken_resources[experiments[failing_experiment]] = failing_experiments[failing_experiment]

            for broken_resource in broken_resources:
                self.coordinator.mark_resource_as_broken(broken_resource, broken_resources[broken_resource])

            for experiment in experiments:
                if not experiment in failing_experiments:
                    # Experiment works!
                    resource = experiments[experiment]
                    if not resource in broken_resources:
                        self.coordinator.mark_resource_as_fixed(resource)

        except:
            traceback.print_exc()
            log.log( ResourcesChecker, log.level.Critical,
                    "Error checking resources of laboratory %s " % address_str)
            log.log_exc(ResourcesChecker, log.level.Critical)

