#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import re

from weblab.core.coordinator.resource import Resource
from weblab.data.experiments import ExperimentInstanceId
import weblab.core.exc as coreExc

COORDINATOR_LABORATORY_SERVERS="core_coordinator_laboratory_servers"
COORDINATOR_EXTERNAL_SERVERS="core_coordinator_external_servers"

class CoordinationConfigurationParser(object):

    EXPERIMENT_INSTANCE_REGEX = r"^(.*)\|(.*)\|(.*)$"
    RESOURCE_INSTANCE_REGEX = r"^(.*)@(.*)$"

    def __init__(self, cfg_manager):
        self._cfg_manager = cfg_manager

    def parse_external_servers(self):
        #
        # {
        #    'experiment_id_str' : [ 'resource_type_name' ]
        # }
        #
        external_servers = self._cfg_manager.get_value(COORDINATOR_EXTERNAL_SERVERS, {})
        for external_server in external_servers:
            external_servers[external_server] = set(external_servers[external_server])
        return external_servers


    def parse_resources_for_experiment_ids(self):
        raw_configuration = self.parse_configuration()

        #
        # {
        #    'experiment_id_str' : set('resource_type_name1', 'resource_type_name2')
        # }
        #
        configuration = self.parse_external_servers()
        for laboratory in raw_configuration:
            laboratory_config = raw_configuration[laboratory]
            for experiment_instance_id in laboratory_config:
                resource_type_name = laboratory_config[experiment_instance_id].resource_type
                experiment_id_str = experiment_instance_id.to_experiment_id().to_weblab_str()
                if not experiment_id_str in configuration:
                    configuration[experiment_id_str] = set()
                configuration[experiment_id_str].add(resource_type_name)

        return configuration

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
                    raise coreExc.CoordinationConfigurationParsingError("Error in coordination parsing: %s doesn't match the regular expression %s" % (experiment_instance, self.EXPERIMENT_INSTANCE_REGEX))

                mo_resource_instance = re.match(self.RESOURCE_INSTANCE_REGEX, resource_instance)
                if mo_resource_instance is None:
                    raise coreExc.CoordinationConfigurationParsingError("Error in coordination parsing: %s doesn't match the regular expression %s" % (resource_instance, self.RESOURCE_INSTANCE_REGEX))

                (
                    inst_name,
                    exp_name,
                    exp_cat_name
                ) = mo_experiment_instance.groups()

                experiment_instance_id = ExperimentInstanceId( inst_name, exp_name, exp_cat_name )

                (
                    resource_instance,
                    resource_type
                ) = mo_resource_instance.groups()

                resource = Resource(resource_type, resource_instance)

                laboratory_configuration[experiment_instance_id] = resource

        return configuration

