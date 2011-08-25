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
import voodoo.log as log
from voodoo.log import logged
import time

import weblab.login.auth as LoginAuth
import weblab.login.delegated_auth as DelegatedLoginAuth
import weblab.login.db.manager as DatabaseManager
import weblab.login.comm.server as LoginFacadeServer
import weblab.login.comm.web_server as WebFacadeServer
import weblab.data.server_type as ServerType
import weblab.login.exc as LoginExceptions
import weblab.db.exc as DbExceptions
import weblab.db.session as DbSession
import weblab.comm.context as RemoteFacadeContext

LOGIN_FAILED_DELAY = 5
NOT_LINKABLE_USERS = 'login_not_linkable_users'
DEFAULT_GROUPS     = 'login_default_groups_for_external_users'
CREATING_EXTERNAL_USERS = 'login_creating_external_users'
LINKING_EXTERNAL_USERS  = 'login_linking_external_users'

class LoginServer(object):

    FACADE_SERVERS = (
                LoginFacadeServer.LoginRemoteFacadeServer,
                WebFacadeServer.LoginWebRemoteFacadeServer
            )

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(LoginServer,self).__init__(*args, **kwargs)
        self._coord_address = coord_address
        self._db_manager    = DatabaseManager.LoginDatabaseManager(cfg_manager)
        self._locator       = locator
        self._cfg_manager   = cfg_manager

        self._facade_servers       = []
        for ServerClass in self.FACADE_SERVERS:
            self._facade_servers.append(ServerClass( self, cfg_manager ))

        for server in self._facade_servers:
            server.start()

        self._external_id_providers = {
                    "FACEBOOK" : DelegatedLoginAuth.Facebook(self._db_manager),
                    "OPENID"   : DelegatedLoginAuth.OpenID(self._db_manager)
                }

    def stop(self):
        if hasattr(super(LoginServer, self), 'stop'):
            super(LoginServer, self).stop()
        for server in self._facade_servers:
            server.stop()

    @logged(log.level.Info, except_for='password')
    def login(self, username, password):
        """ do_login(username, password) -> SessionId 

        raises ( 
            LoginExceptions.UnableToCompleteOperationException, 
            LoginExceptions.InvalidCredentialsException 
        )
        """
        db_session_id = self._validate_local_user(username, password)
        return self._reserve_session(db_session_id)

    def _validate_local_user(self, username, password):
        db_session_id = self._db_manager.check_credentials(username, str(password))

        if isinstance(db_session_id, DbSession.InvalidDatabaseSessionId):
            log.log( LoginServer, log.level.Warning, "Invalid username: %s" % username )
            time.sleep(LOGIN_FAILED_DELAY)
            raise LoginExceptions.InvalidCredentialsException(
                        "Invalid username or password!"
                    )
        elif isinstance(db_session_id, DbSession.NotAuthenticatedSessionId):
            for user_auth in db_session_id.user_auths:
                login_auth = LoginAuth.LoginAuth.create(user_auth)
                if login_auth.authenticate(username, password):
                    log.log( LoginServer, log.level.Debug, "Username: %s with user_auth %s: SUCCESS" % (username, user_auth) )
                    break
                log.log( LoginServer, log.level.Warning, "Username: %s with user_auth %s: FAIL" % (username, user_auth) )
            else :
                raise LoginExceptions.InvalidCredentialsException(
                    "Invalid username or password!"
                )
        return db_session_id

    def _reserve_session(self, db_session_id):
        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        session_id, server_route = ups_server.reserve_session(db_session_id)
        context = RemoteFacadeContext.get_context()
        context.route = server_route
        return session_id

    @logged(log.level.Info)
    def extensible_login(self, system, credentials):
        external_user_id, _ = self._validate_remote_user(system, credentials)
        # It's a valid external user, book it if there is a user linked
        try:
            db_session_id = self._db_manager.check_external_credentials(external_user_id, system)
        except DbExceptions.DbUserNotFoundException:
            raise LoginExceptions.InvalidCredentialsException("%s User ID not found: %s" % (system, external_user_id))

        return self._reserve_session(db_session_id)

    def _validate_remote_user(self, system, credentials):
        system = system.upper()
        if not system in self._external_id_providers:
            raise LoginExceptions.LoginException("Invalid system!")

        external_user_id = self._external_id_providers[system].get_user_id(credentials)
        if external_user_id == "":
            raise LoginExceptions.InvalidCredentialsException(
                "Invalid username or password!"
            )
        external_user = self._external_id_providers[system].get_user(credentials)
        return external_user_id, external_user


    @logged(log.level.Info, except_for="password")
    def grant_external_credentials(self, username, password, system, credentials):
        if not self._cfg_manager.get_value(LINKING_EXTERNAL_USERS, True):
            raise LoginExceptions.LoginException("Linking external users not enabled!")
        not_linkable_users = self._cfg_manager.get_value(NOT_LINKABLE_USERS, [])
        for not_linkable_user in not_linkable_users:
            if username == not_linkable_user:
                raise LoginExceptions.LoginException("Username not linkable!")

        local_db_session_id  = self._validate_local_user(username, password)
        external_user_id, _ = self._validate_remote_user(system, credentials)
        # No exception prior to this: the user is the owner of both username and credentials
        self._db_manager.grant_external_credentials(username, external_user_id, system)
        return self._reserve_session(local_db_session_id)

    @logged(log.level.Info)
    def create_external_user(self, system, credentials):
        if not self._cfg_manager.get_value(CREATING_EXTERNAL_USERS, True):
            raise LoginExceptions.LoginException("Creating external users not enabled!")
        external_user_id, external_user = self._validate_remote_user(system, credentials)
        if external_user is None:
            raise LoginExceptions.LoginException("Creation of external user not supported by delegated login system!")
        group_names = self._cfg_manager.get_value(DEFAULT_GROUPS, [])
        self._db_manager.create_external_user(external_user, external_user_id, system, group_names)
        return self.extensible_login(system, credentials)
