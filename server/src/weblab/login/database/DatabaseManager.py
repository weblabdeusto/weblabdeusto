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

import weblab.login.database.DatabaseGateway as DbGateway
import weblab.database.DatabaseSession as DbSession
import weblab.database.DatabaseAccountManager as DAM
import weblab.exceptions.database.DatabaseExceptions as DbExceptions

import weblab.database.DatabaseConstants as DbConst

class LoginDatabaseManager(object):
    def __init__(self, cfg_manager):
        auth_accounts = self._parse_auth_accounts_credentials(cfg_manager)
        DAM.update_database_accounts(auth_accounts)
        self._auth_gateway = DbGateway.create_auth_gateway(cfg_manager)

    def _parse_auth_accounts_credentials(self, cfg_manager):
        auth_read_username            = cfg_manager.get_value('login_db_users_auth_read_username')
        auth_read_password            = cfg_manager.get_value('login_db_users_auth_read_password')

        return {
            DbConst.AUTH        : {
                DbConst.READ : DAM.DatabaseUserInformation ( auth_read_username, auth_read_password )
            }
        }

    def check_credentials(self,username,password):
        auth_credentials = DAM.get_credentials(DbConst.AUTH)
        try:
            role, user_id, user_auths = self._auth_gateway.check_user_password( auth_credentials, username, password )
        except DbExceptions.DbInvalidUserOrPasswordException,e:
            return DbSession.InvalidDatabaseSessionId()

        if user_auths is None:
            return DbSession.ValidDatabaseSessionId( username, role.name )
        else:
            return DbSession.NotAuthenticatedSessionId( username, role.name, user_auths )

