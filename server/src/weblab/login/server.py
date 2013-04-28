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
import voodoo.log as log
from voodoo.log import logged
import time

import weblab.login.auth as LoginAuth
import weblab.login.delegated_auth as DelegatedLoginAuth

import weblab.login.db.manager as DatabaseManager
from weblab.login.db.gateway import create_auth_gateway
import weblab.login.db.dao.user as dao_user

import weblab.login.comm.server as LoginFacadeServer
import weblab.login.comm.web_server as WebFacadeServer
import weblab.data.server_type as ServerType
import weblab.login.exc as LoginErrors
import weblab.db.exc as DbErrors
import weblab.db.session as DbSession
import weblab.comm.context as RemoteFacadeContext

LOGIN_FAILED_DELAY = 5
NOT_LINKABLE_USERS = 'login_not_linkable_users'
DEFAULT_GROUPS     = 'login_default_groups_for_external_users'
CREATING_EXTERNAL_USERS = 'login_creating_external_users'
LINKING_EXTERNAL_USERS  = 'login_linking_external_users'

"""
This module contains the Login Server. This server will only
manage the authentication (and not the authorization) of the 
users. To this end, it defines that there are two interfaces:

 * One for those systems that can be checked with typical credentials (e.g.,
   using a username a password). Examples of this would be a regular database,
   a LDAP server, or a set of constraints such as "is the user coming from 
   this IP address?". This interface is called "SimpleAuthn".

 * The system, which manages that there is an external system that manages
   the authentication, and some external protocol is required. Examples of this
   are OAuth, OpenID or similar. They all require using a web interface. This
   interface is called "WebProtocolAuthn".

The LoginServer manages both interfaces.
"""

# TODO list:
# - Merge UserAuth and LoginAuth
# - Check if the Facebook and OpenID UserAuths are actually required or not.
# - Remove priority constraint (right now it is a UNIQUE. Use balsamic to avoid being so strict)
# - Check and delete those methods and structures unused after the cleanup.
# - Remove DatabaseManager.

class LoginServer(object):

    FACADE_SERVERS = (
                LoginFacadeServer.LoginRemoteFacadeServer,
                WebFacadeServer.LoginWebRemoteFacadeServer
            )

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(LoginServer,self).__init__(*args, **kwargs)

        log.log( LoginServer, log.level.Info, "Starting Login Server")

        self._coord_address = coord_address
        self._db_gateway    = create_auth_gateway(cfg_manager)
        # TODO: REMOVE db_manager AND USE the gateway
        self._db_manager    = DatabaseManager.LoginDatabaseManager(cfg_manager)
        self._locator       = locator
        self._cfg_manager   = cfg_manager

        self._facade_servers       = []
        for ServerClass in self.FACADE_SERVERS:
            self._facade_servers.append(ServerClass( self, cfg_manager ))

        for server in self._facade_servers:
            server.start()

        self._external_id_providers = {
            dao_user.FacebookUserAuth.NAME : DelegatedLoginAuth.Facebook(self._db_manager),
            dao_user.OpenIDUserAuth.NAME   : DelegatedLoginAuth.OpenID(self._db_manager)
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
            LoginErrors.UnableToCompleteOperationError,
            LoginErrors.InvalidCredentialsError
        )
        """
        db_session_id = self._validate_simple_interface(username, password)
        return self._reserve_session(db_session_id)


    def _validate_simple_authn(self, username, credentials):
        """
        When the login() method is called, this method is used with the 
        username and credentials (e.g., password, IP address, etc.). This
        method will only check the SimpleAuthn instances.
        """
        user_auths = self._db_gateway.retrieve_auth_types(username)

        errors = False

        for user_auth in user_auths:
            # Take only those auth types that use a simple interface
            if user_auth.is_simple_authn():
                simple_login_auth = LoginAuth.LoginAuth.create(user_auth)
    
                # With each user auth, try to authenticate the user.
                try:
                    authenticated = login_auth.authenticate(username, credentials)
                except:
                    # If there is an error, the user could not be authenticated.
                    log.log( LoginServer, log.level.Warning, "Username: %s with user_auth %s: ERROR" % (username, user_auth) )
                    log.log_exc( LoginServer, log.level.Warning)
                    errors = True
                    continue
                
                if authenticated:
                    # If authenticated, return that it was correctly authenticated.
                    log.log( LoginServer, log.level.Debug, "Username: %s with user_auth %s: SUCCESS" % (username, user_auth) )
                    return DbSession.ValidDatabaseSessionId( username, None ) # TODO: role.name

                else:
                    # If not authenticated, log it and continue with the next user_auth.
                    log.log( LoginServer, log.level.Warning, "Username: %s with user_auth %s: FAIL" % (username, user_auth) )
        
        if errors:
            # Raise error: there was a server problem and this might be the reason for not 
            # authenticating the user. Examples: LDAP server is down, there is an error in the
            # local database or so.
            raise LoginErrors.LoginError( "Error checking credentials. Contact administrators!" )

        # Add a timeout when fails to authenticate in a normal way.
        time.sleep(LOGIN_FAILED_DELAY)

        raise LoginErrors.InvalidCredentialsError( "Invalid username or password!" )

# TODO: remove me
#     def _validate_local_user(self, username, password):
#         db_session_id = self._db_manager.check_credentials(username, str(password))
# 
#         if isinstance(db_session_id, DbSession.InvalidDatabaseSessionId):
#             log.log( LoginServer, log.level.Warning, "Invalid username: %s" % username )
#             time.sleep(LOGIN_FAILED_DELAY)
#             raise LoginErrors.InvalidCredentialsError(
#                         "Invalid username or password!"
#                     )
#         elif isinstance(db_session_id, DbSession.NotAuthenticatedSessionId):
#             for user_auth in db_session_id.user_auths:
#                 login_auth = LoginAuth.LoginAuth.create(user_auth)
#                 if login_auth.authenticate(username, password):
#                     log.log( LoginServer, log.level.Debug, "Username: %s with user_auth %s: SUCCESS" % (username, user_auth) )
#                     break
#                 log.log( LoginServer, log.level.Warning, "Username: %s with user_auth %s: FAIL" % (username, user_auth) )
#             else :
#                 raise LoginErrors.InvalidCredentialsError(
#                     "Invalid username or password!"
#                 )
#         return db_session_id

    def _reserve_session(self, db_session_id):
        """ Contact the Core server and reserve a session there that we will return
        the user. """
        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        session_id, server_route = ups_server.reserve_session(db_session_id)
        context = RemoteFacadeContext.get_context()
        context.route = server_route
        if hasattr(session_id, 'id'):
            context.session_id = session_id.id
        else:
            context.session_id = session_id
        return session_id

    @logged(log.level.Info)
    def extensible_login(self, system, credentials):
        external_user_id, _ = self._validate_remote_user(system, credentials)
        # It's a valid external user, book it if there is a user linked
        try:
            db_session_id = self._db_manager.check_external_credentials(external_user_id, system)
        except DbErrors.DbUserNotFoundError:
            raise LoginErrors.InvalidCredentialsError("%s User ID not found: %s" % (system, external_user_id))

        return self._reserve_session(db_session_id)

    def _validate_remote_user(self, system, credentials):
        system = system.upper()
        if not system in self._external_id_providers:
            raise LoginErrors.LoginError("Invalid system!")

        external_user_id = self._external_id_providers[system].get_user_id(credentials)
        if external_user_id == "":
            raise LoginErrors.InvalidCredentialsError(
                "Invalid username or password!"
            )
        external_user = self._external_id_providers[system].get_user(credentials)
        return external_user_id, external_user


    @logged(log.level.Info, except_for="password")
    def grant_external_credentials(self, username, password, system, credentials):
        """ Links an existing user to the new user. """

        if not self._cfg_manager.get_value(LINKING_EXTERNAL_USERS, True):
            raise LoginErrors.LoginError("Linking external users not enabled!")
        not_linkable_users = self._cfg_manager.get_value(NOT_LINKABLE_USERS, [])
        for not_linkable_user in not_linkable_users:
            if username == not_linkable_user:
                raise LoginErrors.LoginError("Username not linkable!")

        local_db_session_id  = self._validate_local_user(username, password)
        external_user_id, _ = self._validate_remote_user(system, credentials)
        # No exception prior to this: the user is the owner of both username and credentials
        self._db_gateway.grant_external_credentials(username, external_user_id, system)
        return self._reserve_session(local_db_session_id)

    @logged(log.level.Info)
    def create_external_user(self, system, credentials):
        """ Create a new user using an external system. """

        if not self._cfg_manager.get_value(CREATING_EXTERNAL_USERS, True):
            raise LoginErrors.LoginError("Creating external users not enabled!")
        external_user_id, external_user = self._validate_remote_user(system, credentials)
        if external_user is None:
            raise LoginErrors.LoginError("Creation of external user not supported by delegated login system!")
        group_names = self._cfg_manager.get_value(DEFAULT_GROUPS, [])
        self._db_gateway.create_external_user(external_user, external_user_id, system, group_names)
        return self.extensible_login(system, credentials)
