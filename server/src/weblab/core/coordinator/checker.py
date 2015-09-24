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
from __future__ import print_function, unicode_literals

import traceback

import voodoo.log as log
from voodoo.gen import CoordAddress

class ResourcesChecker(object):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.locator     = coordinator.locator
        self.current_lab = None

    def check(self):
        try:
            experiments_per_laboratory = self.coordinator.list_laboratories_addresses()

            # Use a common broken_resources to avoid endless loops if a resource is registered
            # in labs in more than one laboratory server (and one might state that it works while
            # other might state that it doesn't).
            broken_resources = {}
            for laboratory_address_str in experiments_per_laboratory:
                self.current_lab = laboratory_address_str
                new_broken_resources = self.check_laboratory(laboratory_address_str, experiments_per_laboratory[laboratory_address_str])
                for broken_resource in new_broken_resources:
                    if broken_resource in broken_resources:
                        broken_resources[broken_resource] += ';' + new_broken_resources[broken_resource]
                    else:
                        broken_resources[broken_resource] = new_broken_resources[broken_resource]

            all_notifications = {
                # (recipient1, recipient2) : [message1, message2, message3],
                # (recipient1, ) : [message4, message5],
                # (recipient3, ) : [message6, message7],
            }

            for laboratory_address_str in experiments_per_laboratory:
                experiments = experiments_per_laboratory[laboratory_address_str]
                for experiment in experiments:
                    laboratory_resource = experiments[experiment]
                    if laboratory_resource in broken_resources:
                        notifications = self.coordinator.mark_resource_as_broken(laboratory_resource, broken_resources[laboratory_resource])
                    else:
                        notifications = self.coordinator.mark_resource_as_fixed(laboratory_resource)

                    for recipients in notifications:
                        if recipients in all_notifications:
                            all_notifications[recipients].extend(notifications[recipients])
                        else:
                            all_notifications[recipients] = list(notifications[recipients])

            if all_notifications:
                self.coordinator.notify_status(all_notifications)
        except:
            traceback.print_exc()
            log.log( ResourcesChecker, log.level.Critical,
                    "Error checking resources.")
            log.log_exc(ResourcesChecker, log.level.Critical)

    def check_laboratory(self, address_str, experiments):
        """ Checks in that laboratory address which experiments are broken and which ones are working.

        :param address_str: laboratory address, e.g. "laboratory:general_laboratory@server1"
        :param experiments: dictionary of experiments: resources, e.g. { "exp1|ud-fpga|FPGA experiments" : "fpga1@fpga boards"}
        """
        broken_resources = {
            # resource_id : error_message
        }

        try:
            address = CoordAddress.translate(address_str)
            server = self.locator[address]
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

        except:
            traceback.print_exc()
            log.log( ResourcesChecker, log.level.Critical,
                    "Error checking resources of laboratory %s " % address_str)
            log.log_exc(ResourcesChecker, log.level.Critical)
        
        return broken_resources

