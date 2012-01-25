#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

from voodoo.log import logged
import weblab.comm.manager as RFM
import weblab.data.client_address as ClientAddress

import weblab.login.exc as LoginExceptions
import weblab.exc as WebLabExceptions
import voodoo.gen.exceptions.exceptions as VoodooExceptions

import weblab.login.comm.codes as LFCodes

EXCEPTIONS = (
        #
        # EXCEPTION                                   CODE                                               PROPAGATE TO CLIENT
        #
        (LoginExceptions.InvalidCredentialsException, LFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE, True),
        (LoginExceptions.LoginException,              LFCodes.LOGIN_SERVER_EXCEPTION_CODE,               False),
        (WebLabExceptions.WebLabException,            LFCodes.WEBLAB_GENERAL_EXCEPTION_CODE,             False),
        (VoodooExceptions.GeneratorException,         LFCodes.VOODOO_GENERAL_EXCEPTION_CODE,             False),
        (Exception,                                   LFCodes.PYTHON_GENERAL_EXCEPTION_CODE,             False)
    )

ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS = 'login_facade_trusted_addresses'
DEFAULT_ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS = ('127.0.0.1',)

class AbstractLoginRemoteFacadeManager(RFM.AbstractRemoteFacadeManager):
    @logged()
    def login_based_on_client_address(self, username, client_address):
        """ login_based_on_client_address(username, client_address) -> SessionID
            raises LoginException, InvalidCredentialsException
        """
        current_client_address = self._get_client_address()
        addresses_calling_this_method = self._cfg_manager.get_value(ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS, DEFAULT_ADDRESSES_CALLING_LOGIN_BASED_ON_CLIENT_ADDRESS)
        if current_client_address in addresses_calling_this_method:
            return self._login_impl( username, ClientAddress.ClientAddress(client_address) )
        else:
            return self._raise_exception(
                    LFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE,
                    "You can't login from IP address: %s" % current_client_address
                )

    @logged(except_for='password')
    def login(self, username, password):
        """ login(username, password) -> SessionID
            raises LoginException, InvalidCredentialsException
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


class LoginRemoteFacadeManagerZSI(RFM.AbstractZSI, AbstractLoginRemoteFacadeManager):
    pass

class LoginRemoteFacadeManagerJSON(RFM.AbstractJSON, AbstractLoginRemoteFacadeManager):
    pass

class LoginRemoteFacadeManagerXMLRPC(RFM.AbstractXMLRPC, AbstractLoginRemoteFacadeManager):
    pass

