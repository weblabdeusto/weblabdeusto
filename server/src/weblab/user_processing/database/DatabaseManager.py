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

import weblab.user_processing.database.DatabaseGateway as DbGateway
import weblab.database.DatabaseAccountManager as DAM
import weblab.database.DatabaseConstants as DbConst

class UserProcessingDatabaseManager(object):
    def __init__(self, cfg_manager):
        super(UserProcessingDatabaseManager, self).__init__()

        regular_accounts = self._parse_regular_accounts_credentials(cfg_manager)
        DAM.update_database_accounts(regular_accounts)
        self._gateway      = DbGateway.create_gateway(cfg_manager)

    def _parse_regular_accounts_credentials(self, cfg_manager):
        student_read_username         = cfg_manager.get_value('core_db_users_student_read_username')
        student_read_password         = cfg_manager.get_value('core_db_users_student_read_password')
        student_write_username        = cfg_manager.get_value('core_db_users_student_write_username')
        student_write_password        = cfg_manager.get_value('core_db_users_student_write_password')

        professor_read_username       = cfg_manager.get_value('core_db_users_professor_read_username')
        professor_read_password       = cfg_manager.get_value('core_db_users_professor_read_password')
        professor_write_username      = cfg_manager.get_value('core_db_users_professor_write_username')
        professor_write_password      = cfg_manager.get_value('core_db_users_professor_write_password')

        administrator_read_username   = cfg_manager.get_value('core_db_users_administrator_read_username')
        administrator_read_password   = cfg_manager.get_value('core_db_users_administrator_read_password')
        administrator_write_username  = cfg_manager.get_value('core_db_users_administrator_write_username')
        administrator_write_password  = cfg_manager.get_value('core_db_users_administrator_write_password')

        externalentity_read_username  = cfg_manager.get_value('core_db_users_externalentity_read_username')
        externalentity_read_password  = cfg_manager.get_value('core_db_users_externalentity_read_password')
        externalentity_write_username = cfg_manager.get_value('core_db_users_externalentity_write_username')
        externalentity_write_password = cfg_manager.get_value('core_db_users_externalentity_write_password')

        return {
            DbConst.STUDENT     : {
                DbConst.READ : DAM.DatabaseUserInformation ( student_read_username, student_read_password ),
                DbConst.WRITE : DAM.DatabaseUserInformation ( student_write_username, student_write_password )
            },
            DbConst.PROFESSOR   : {
                DbConst.READ : DAM.DatabaseUserInformation ( professor_read_username, professor_read_password ),
                DbConst.WRITE : DAM.DatabaseUserInformation ( professor_write_username, professor_write_password )

            },
            DbConst.ADMINISTRATOR   : {
                DbConst.READ : DAM.DatabaseUserInformation ( administrator_read_username, administrator_read_password ),
                DbConst.WRITE : DAM.DatabaseUserInformation ( administrator_write_username, administrator_write_password )
            },
            DbConst.EXTERNAL_ENTITY : {
                DbConst.READ : DAM.DatabaseUserInformation ( externalentity_read_username, externalentity_read_password ),
                DbConst.WRITE : DAM.DatabaseUserInformation ( externalentity_write_username, externalentity_write_password )
            }
        }
   
    def get_available_experiments(self, session_id):
        credentials = DAM.get_credentials(session_id.role)
        username    = session_id.username
        user = self._gateway.get_user_by_name( credentials, username )
        return self._gateway.list_experiments( credentials, user.id )
    
    def store_experiment_usage(self, session_id, experiment_usage):
        credentials = DAM.get_credentials(session_id.role)
        username    = session_id.username
        user = self._gateway.get_user_by_name( credentials, username )
        return self._gateway.store_experiment_usage( credentials, user.id, experiment_usage )

    def retrieve_user_information(self, session_id):
        credentials = DAM.get_credentials(session_id.role)
        username    = session_id.username
        user = self._gateway.get_user_by_name( credentials, username )
        return user.to_business()

