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
        """ Checks in that laboratory address which experiments are broken and which ones are working.

        :param address_str: laboratory address, e.g. "laboratory:general_laboratory@server1"
        :param experiments: dictionary of experiments: resources, e.g. { "exp1|ud-fpga|FPGA experiments" : "fpga1@fpga boards"}
        """
        try:
            laboratory_resources = set()
            for experiment in experiments:
                laboratory_resources.add(experiments[experiment])

            broken_resources = {}
            address = CoordAddress.CoordAddress.translate_address(address_str)
            server = self.locator.get_server_from_coordaddr(address, ServerType.Laboratory)
            failing_experiments = server.check_experiments_resources()
            #
            # failing_experiments is a dictionary such as:
            # {
            #     experiment_instance_id : error_message
            # }
            # 
            for failing_experiment in failing_experiments:
                if not failing_experiment in experiments:
                    log.log( ResourcesChecker, log.level.Error,
                            "Laboratory server %s reported that experiment %s was failing; however this laboratory does NOT manage this experiment. Attack?" % (address_str, failing_experiment))
                    continue

                # 
                # The error for a resource will be concatenated
                # 
                broken_resource = experiments[failing_experiment]
                error_message   = failing_experiments[failing_experiment]
                if broken_resource in broken_resources:
                    broken_resources[broken_resource] = broken_resources[broken_resource] + ';' + error_message
                else:
                    broken_resources[broken_resource] = error_message

            for laboratory_resource in laboratory_resources:
                if laboratory_resource in broken_resources:
                    self.coordinator.mark_resource_as_broken(laboratory_resource, broken_resources[laboratory_resource])
                else:
                    self.coordinator.mark_resource_as_fixed(laboratory_resource)

        except:
            traceback.print_exc()
            log.log( ResourcesChecker, log.level.Critical,
                    "Error checking resources of laboratory %s " % address_str)
            log.log_exc(ResourcesChecker, log.level.Critical)

