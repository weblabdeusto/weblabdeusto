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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import re

from weblab.core.coordinator.Resource import Resource
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.exceptions.core.UserProcessingExceptions as UserProcessingExceptions

COORDINATOR_LABORATORY_SERVERS="core_coordinator_laboratory_servers"

class CoordinationConfigurationParser(object):

    EXPERIMENT_INSTANCE_REGEX = r"^(.*)\|(.*)\|(.*)$"
    RESOURCE_INSTANCE_REGEX = r"^(.*)@(.*)$"

    def __init__(self, cfg_manager):
        self._cfg_manager = cfg_manager

    def parse_configuration(self):
        # 
        # configuration = {
        #      "laboratory1:WL_SERVER1@WL_MACHINE1" : {
        #                 ExperimentInstanceId("exp1", "ud-pld", "PLD Experiments") : ("pld1", "ud-pld-boards")
        #      }
        # }
        # 
        configuration = {}

        laboratory_servers = self._cfg_manager.get_value(COORDINATOR_LABORATORY_SERVERS)
        for laboratory_server_coord_address_str in laboratory_servers:
            experiment_instances = laboratory_servers[laboratory_server_coord_address_str]

            laboratory_configuration = {}
            configuration[laboratory_server_coord_address_str] = laboratory_configuration

            for experiment_instance in experiment_instances:
                resource_instance = experiment_instances[experiment_instance]
                mo_experiment_instance = re.match(self.EXPERIMENT_INSTANCE_REGEX, experiment_instance)
                if mo_experiment_instance is None:
                    raise UserProcessingExceptions.CoordinationConfigurationParsingException("Error in coordination parsing: %s doesn't match the regular expression %s" % (experiment_instance, self.EXPERIMENT_INSTANCE_REGEX))

                mo_resource_instance = re.match(self.RESOURCE_INSTANCE_REGEX, resource_instance)
                if mo_resource_instance is None:
                    raise UserProcessingExceptions.CoordinationConfigurationParsingException("Error in coordination parsing: %s doesn't match the regular expression %s" % (resource_instance, self.RESOURCE_INSTANCE_REGEX))

                (
                    inst_name,
                    exp_name,
                    exp_cat_name
                ) = mo_experiment_instance.groups()

                experiment_instance_id = ExperimentInstanceId.ExperimentInstanceId( inst_name, exp_name, exp_cat_name )

                (
                    resource_instance,
                    resource_type
                ) = mo_resource_instance.groups()

                resource = Resource(resource_type, resource_instance)
                 
                laboratory_configuration[experiment_instance_id] = resource

        return configuration

