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

import weblab.core.db.gateway as DbGateway

class UserProcessingDatabaseManager(object):
    
    def __init__(self, cfg_manager):
        super(UserProcessingDatabaseManager, self).__init__()
        self._gateway = DbGateway.create_gateway(cfg_manager)

    def retrieve_user_information(self, session_id):
        return self._gateway.get_user_by_name( session_id.username )
   
    def get_available_experiments(self, session_id):
        return self._gateway.list_experiments( session_id.username )
    
    def store_experiment_usage(self, session_id, reservation_info, experiment_usage):
        return self._gateway.store_experiment_usage( session_id.username, reservation_info, experiment_usage )

    def is_access_forward(self, session_id):
        return self._gateway.is_access_forward( session_id.username)

    def finish_experiment_usage(self, reservation_id, end_date, last_command):
        """ Tries to finish the experiment usage (adding the end_date and appending the finish command). Returns True if it was added successfully, false otherwise """
        return self._gateway.finish_experiment_usage( reservation_id, end_date, last_command )

    def append_command(self, reservation_id, command):
        """ Tries to append a command. Returns True if it was added successfully, false otherwise """
        return self._gateway.append_command( reservation_id, command )

    def update_command(self, command_id, response, end_timestamp):
        """ Tries to update a command. Returns True if it was added successfully, false otherwise """
        return self._gateway.update_command( command_id, response, end_timestamp )

    def append_file(self, reservation_id, file_sent):
        """ Tries to append a file. Returns True if it was added successfully, false otherwise """
        return self._gateway.append_file( reservation_id, file_sent )

    def update_file(self, file_id, response, end_timestamp):
        """ Tries to update a file. Returns True if it was added successfully, false otherwise """
        return self._gateway.update_file( file_id, response, end_timestamp )
   
    def update_groups(self, session_id, id, name, parent_id):
        """
        Updates the specified group.
        Returns True if the update succeeded, false otherwise."
        """
        return self._gateway.update_groups(session_id.username, id, name, parent_id)
   
    def get_groups(self, session_id, parent_id=None):
        return self._gateway.get_groups(session_id.username, parent_id)
    
    def get_roles(self, session_id):
        """ Retrieves every role (through the database gateway) """
        return self._gateway.get_roles(session_id.username)
    
    def get_users(self, session_id):
        """ Retrieves the users (through the database gateway) """
        return self._gateway.get_users(session_id.username)
    
    def get_experiments(self, session_id):
        return self._gateway.get_experiments(session_id.username)
    
    def get_experiment_uses(self, session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by ):
        return self._gateway.get_experiment_uses( session_id.username, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by )
    
    def get_user_permissions(self, session_id):
        return self._gateway.get_user_permissions( session_id.username )
    
    def get_permission_types(self, session_id):
        """ Retrieves the permission types (through the database gateway) """
        return self._gateway.get_permission_types( session_id.username )

    def _delete_all_uses(self):
        return self._gateway._delete_all_uses()
