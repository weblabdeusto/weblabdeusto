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
#

from voodoo.log import logged
import weblab.comm.manager as RFM

import weblab.core.login.exc as LoginErrors
import weblab.exc as WebLabErrors
import voodoo.gen.exceptions.exceptions as VoodooErrors

import weblab.login.comm.codes as LFCodes

EXCEPTIONS = (
        #
        # EXCEPTION                                   CODE                                               PROPAGATE TO CLIENT
        #
        (LoginErrors.InvalidCredentialsError, LFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE, True),
        (LoginErrors.LoginError,              LFCodes.LOGIN_SERVER_EXCEPTION_CODE,               False),
        (WebLabErrors.WebLabError,            LFCodes.WEBLAB_GENERAL_EXCEPTION_CODE,             False),
        (VoodooErrors.GeneratorError,         LFCodes.VOODOO_GENERAL_EXCEPTION_CODE,             False),
        (Exception,                                   LFCodes.PYTHON_GENERAL_EXCEPTION_CODE,             False)
    )

ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS = 'login_facade_trusted_addresses'
DEFAULT_ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS = ('127.0.0.1',)

class AbstractLoginRemoteFacadeManager(RFM.AbstractRemoteFacadeManager):
    @logged()
    def login_based_on_client_address(self, username, client_address):
        """ login_based_on_client_address(username, client_address) -> SessionID
            raises LoginError, InvalidCredentialsError
        """
        current_client_address = self._get_client_address()
        addresses_calling_this_method = self._cfg_manager.get_value(ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS, DEFAULT_ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS)
        if current_client_address in addresses_calling_this_method:
            return self._login_impl( username ) # TODO
        else:
            return self._raise_exception(
                    LFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE,
                    "You can't login from IP address: %s" % current_client_address
                )

    @logged(except_for='password')
    def login(self, username, password):
        """ login(username, password) -> SessionID
            raises LoginError, InvalidCredentialsError
        """
        return self._login_impl(username, password)

    @RFM.check_exceptions(EXCEPTIONS)
    def _login_impl(self, username, password):
        return self._server.login(username, password)

    @logged()
    def login_based_on_other_credentials(self, system, credentials):
        """ login_based_on_other_credentials(system, credentials) -> SessionID """
        return self._extensible_login_impl(system, credentials)

    @RFM.check_exceptions(EXCEPTIONS)
    def _extensible_login_impl(self, system, credentials):
        return self._server.extensible_login(system, credentials)

    @logged(except_for='password')
    def grant_external_credentials(self, username, password, system, credentials):
        """ grant_external_credentials(username, password, system, credentials) -> SessionID """
        return self._grant_external_credentials_impl(username, password, system, credentials)

    @RFM.check_exceptions(EXCEPTIONS)
    def _grant_external_credentials_impl(self, username, password, system, credentials):
        return self._server.grant_external_credentials(username, password, system, credentials)

    @logged(except_for='password')
    def create_external_user(self, system, credentials):
        """ create_external_user(system, credentials) -> SessionID """
        return self._create_external_user_impl(system, credentials)

    @RFM.check_exceptions(EXCEPTIONS)
    def _create_external_user_impl(self, system, credentials):
        return self._server.create_external_user(system, credentials)


class LoginRemoteFacadeManagerJSON(RFM.AbstractJSON, AbstractLoginRemoteFacadeManager):
    pass


