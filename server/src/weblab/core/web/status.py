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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

from flask import render_template

from weblab.configuration_doc import COORDINATOR_IMPL
from weblab.core.wl import weblab_api
import weblab.core.coordinator.config_parser as CoordinationConfigurationParser
from weblab.core.web.quickadmin import check_credentials

@weblab_api.route_web('/status/global.json')
@check_credentials
def status_global():
    if weblab_api.config.get(COORDINATOR_IMPL) != 'redis':
        return "This method is only available on Redis", 404

    experiments = get_experiments()

    return weblab_api.jsonify(experiments=experiments)


@weblab_api.route_web('/status/experiments/<category_name>/<experiment_name>.json')
@check_credentials
def experiment_status(category_name, experiment_name):
    if weblab_api.config.get(COORDINATOR_IMPL) != 'redis':
        return "This method is only available on Redis", 404

    experiment_id = '{}@{}'.format(experiment_name, category_name)
    experiments = get_experiments()
    if category_name not in experiments:
        return "experiment not found", 404

    experiment = experiments[category_name].get(experiment_id)
    if experiment is None:
        return "experiment not found", 404

    return weblab_api.jsonify(experiment=experiment)

@weblab_api.route_web('/status/global.html')
@check_credentials
def status_global_html():
    if weblab_api.config.get(COORDINATOR_IMPL) != 'redis':
        return "This method is only available on Redis", 404

    experiments = get_experiments()

    return render_template('core_web/status_global.html', experiments=experiments)


@weblab_api.route_web('/status/experiments/<category_name>/<experiment_name>.html')
@check_credentials
def experiment_status_html(category_name, experiment_name):
    if weblab_api.config.get(COORDINATOR_IMPL) != 'redis':
        return "This method is only available on Redis", 404

    experiment_id = '{}@{}'.format(experiment_name, category_name)
    experiments = get_experiments()
    if category_name not in experiments:
        return "experiment not found", 404

    experiment = experiments[category_name].get(experiment_id)
    if experiment is None:
        return "experiment not found", 404

    return render_template('core_web/status_global.html', experiments={category_name: {experiment_id: experiment}})


def get_experiments():
    coordination_configuration_parser = CoordinationConfigurationParser.CoordinationConfigurationParser(weblab_api.config)
    configuration = coordination_configuration_parser.parse_configuration()

    experiments = {
        # cat_id:
        #    experiment_id: {
        #        instance_id: {
        #            'working': True/False
        #            'resource': {
        #                'resource_instance': 'foo',
        #                'resource_type': 'bar'
        #            }
        #        }
        #    }
        # }
    }

    resources_manager = weblab_api.server_instance._coordinator.resources_manager
    available_resources = resources_manager.list_working_resource_instances()

    for laboratory_server_coord_address_str in configuration:
        experiment_instance_config = configuration[laboratory_server_coord_address_str]
        for experiment_instance_id in experiment_instance_config:
            resource = experiment_instance_config[experiment_instance_id]
            cat_name = experiment_instance_id.cat_name
            if cat_name not in experiments:
                experiments[cat_name] = {}

            experiment_id = experiment_instance_id.to_experiment_id().to_weblab_str()
            if experiment_id not in experiments[cat_name]:
                experiments[cat_name][experiment_id] = {}
            
            resource_found = False
            for available_resource in available_resources:
                if available_resource.resource_type == resource.resource_type and available_resource.resource_instance == resource.resource_instance:
                    resource_found = True
                    break

            if not resource_found:
                error_messages = resources_manager.get_resource_error(resource)
            else:
                error_messages = []

            experiments[cat_name][experiment_id][experiment_instance_id.inst_name] = {
                'working': resource_found,
                'error_messages': error_messages,
                'laboratory_server': laboratory_server_coord_address_str,
                'resource': {
                    'resource_type': resource.resource_type,
                    'resource_instance': resource.resource_instance,
                }
            }

    return experiments

