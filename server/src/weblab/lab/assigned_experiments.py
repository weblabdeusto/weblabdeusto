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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

from weblab.data.experiments import ExperimentInstanceId
import weblab.lab.experiment_handler as ExperimentHandler
import weblab.lab.exc as LaboratoryErrors

class AssignedExperiments(object):
    """
    [?
    Registry of every Experiment that has been assigned to a specific Laboratory Server.
    Through it, it is possible to execute certain operations on Experiments through their
    experiment id, such as Reserve.
    ]
    """

    def __init__(self):
        super(AssignedExperiments, self).__init__()
        self._clear()

    def _clear(self):
        self._experiments      = {
                #It's something like:
                #'category': {
                #       'experiment_name' : {
                #              'instance0' : ExperimentHandler
                #       }
                #}
            }

    def add_server(self, exp_inst_id, experiment_coord_address, experiment_info):
        """
        Registers an Experiment server into this registry. They are organized in a dictionary
        by categories, and within the category by experiment.
        """

        by_category = self._experiments.get( exp_inst_id.cat_name )
        if by_category == None:
            by_category = {}
            self._experiments[exp_inst_id.cat_name] = by_category

        by_experiment = by_category.get( exp_inst_id.exp_name )
        if by_experiment == None:
            by_experiment = {}
            by_category[exp_inst_id.exp_name] = by_experiment

        by_instance = by_experiment.get( exp_inst_id.inst_name )
        if by_instance != None:
            raise LaboratoryErrors.ExperimentAlreadyFoundError(
                "Experiment instance already found in server"
            )

        by_experiment[exp_inst_id.inst_name] = ExperimentHandler.ExperimentHandler( experiment_coord_address, experiment_info['checkers'])
        if 'api' in experiment_info:
            by_experiment[exp_inst_id.inst_name].api = experiment_info['api']
        if 'manages_polling' in experiment_info:
            by_experiment[exp_inst_id.inst_name].manages_polling = experiment_info['manages_polling']

    def list_experiment_instance_ids(self):
        experiment_instance_ids = []
        for category_name in self._experiments:
            experiments = self._experiments[category_name]
            for experiment_name in experiments:
                instances = experiments[experiment_name]
                for instance_name in instances:
                    exp_instance_id = ExperimentInstanceId(instance_name, experiment_name, category_name)
                    experiment_instance_ids.append(exp_instance_id)

        return experiment_instance_ids

    def reserve_experiment(self, experiment_instance_id, lab_sess_id):
        experiment_handler = self._retrieve_experiment_handler( experiment_instance_id )
        experiment_handler.reserve(lab_sess_id)
        return experiment_handler.experiment_coord_address


    def free_experiment(self, experiment_instance_id):
        exp_handler = self._retrieve_experiment_handler( experiment_instance_id )
        if not exp_handler.free():
            raise LaboratoryErrors.AlreadyFreedExperimentError( "Experiment was already free" )

    def get_coord_address(self, experiment_instance_id):
        exp_handler = self._retrieve_experiment_handler( experiment_instance_id )
        return exp_handler.experiment_coord_address

    def get_lab_session_id(self, experiment_instance_id):
        exp_handler = self._retrieve_experiment_handler( experiment_instance_id )
        return exp_handler.lab_session_id

    def manages_polling(self, experiment_instance_id):
        """
        Retrieve whether the current experiment manages polling by its own or not
        """
        return self._retrieve_experiment_handler( experiment_instance_id ).manages_polling

    def get_api(self, experiment_instance_id):
        """
        Gets the API version that the specified experiment instance is currently using.
        """
        return self._retrieve_experiment_handler( experiment_instance_id ).api

    def set_api(self, experiment_instance_id, api):
        """

        """
        self._retrieve_experiment_handler( experiment_instance_id ).api = api

    def _retrieve_experiment_handler(self, experiment_instance_id):
        inst_name = experiment_instance_id.inst_name
        exp_name  = experiment_instance_id.exp_name
        cat_name  = experiment_instance_id.cat_name
        try:
            return self._experiments[cat_name][exp_name][inst_name]
        except KeyError:
            raise LaboratoryErrors.ExperimentNotFoundError( "Experiment instance not found! %s" % experiment_instance_id )

    def get_is_up_and_running_handlers(self, experiment_instance_id):
        exp_handler = self._retrieve_experiment_handler( experiment_instance_id )
        return exp_handler.is_up_and_running_handlers
