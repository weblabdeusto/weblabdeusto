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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import weblab.user_processing.database.DatabaseGateway as DbGateway

class UserProcessingDatabaseManager(object):
    
    def __init__(self, cfg_manager):
        super(UserProcessingDatabaseManager, self).__init__()
        self._gateway = DbGateway.create_gateway(cfg_manager)

    def retrieve_user_information(self, session_id):
        return self._gateway.get_user_by_name( session_id.username )
   
    def get_available_experiments(self, session_id):
        return self._gateway.list_experiments( session_id.username )
    
    def store_experiment_usage(self, session_id, experiment_usage):
        return self._gateway.store_experiment_usage( session_id.username, experiment_usage )