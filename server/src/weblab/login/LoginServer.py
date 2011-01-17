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
import voodoo.LogLevel as LogLevel
import time

import weblab.login.LoginAuth as LoginAuth
import weblab.login.database.DatabaseManager as DatabaseManager
import weblab.login.facade.LoginFacadeServer as LoginFacadeServer
import weblab.data.ServerType as ServerType
import weblab.exceptions.login.LoginExceptions as LoginExceptions
import weblab.database.DatabaseSession as DbSession
import weblab.facade.RemoteFacadeContext as RemoteFacadeContext

LOGIN_FAILED_DELAY=5

class LoginServer(object):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(LoginServer,self).__init__(*args, **kwargs)
        self._coord_address = coord_address
        self._db_manager    = DatabaseManager.LoginDatabaseManager(cfg_manager)
        self._locator       = locator

        self._facade_server = LoginFacadeServer.LoginRemoteFacadeServer( self, cfg_manager ) 
        self._facade_server.start()

    def stop(self):
        if hasattr(super(LoginServer, self), 'stop'):
            super(LoginServer, self).stop()
        self._facade_server.stop()

    @logged(LogLevel.Info, except_for='password')
    def login(self, username, password):
        """ do_login(username, password) -> SessionId 

        raises ( 
            LoginExceptions.UnableToCompleteOperationException, 
            LoginExceptions.InvalidCredentialsException 
        )
        """
        db_session_id = self._db_manager.check_credentials(username, str(password))

        if isinstance(db_session_id, DbSession.InvalidDatabaseSessionId):
            log.log( LoginServer, log.LogLevel.Warning, "Invalid username: %s" % username )
            time.sleep(LOGIN_FAILED_DELAY)
            raise LoginExceptions.InvalidCredentialsException(
                        "Invalid username or password!"
                    )
        elif isinstance(db_session_id, DbSession.NotAuthenticatedSessionId):
            for user_auth in db_session_id.user_auths:
                login_auth = LoginAuth.LoginAuth.create(user_auth)
                if login_auth.authenticate(username, password):
                    log.log( LoginServer, log.LogLevel.Debug, "Username: %s with user_auth %s: SUCCESS" % (username, user_auth) )
                    break
                log.log( LoginServer, log.LogLevel.Warning, "Username: %s with user_auth %s: FAIL" % (username, user_auth) )
            else :
                raise LoginExceptions.InvalidCredentialsException(
                    "Invalid username or password!"
                )

        ups_server = self._locator.get_easy_server(ServerType.UserProcessing)
        session_id, server_route = ups_server.reserve_session(db_session_id)
        context = RemoteFacadeContext.get_context()
        context.route = server_route
        return session_id

    @logged(LogLevel.Info, except_for='password')
    def extensible_login(self, system, credentials):
        pass

