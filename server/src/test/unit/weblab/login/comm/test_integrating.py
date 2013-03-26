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
import sys
import unittest

try:
    import ZSI
    from weblab.login.comm.generated.loginweblabdeusto_client import loginweblabdeustoSOAP as LoginWebLabDeustoSOAP
except ImportError:
    pass

from test.util.ports import new as new_port

import weblab.configuration_doc as configuration_doc

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
import voodoo.sessions.session_id as SessionId

import voodoo.configuration as ConfigurationManager
import test.unit.configuration as configuration

from test.util.module_disposer import uses_module

import weblab.login.comm.codes as LoginRFCodes
import weblab.comm.server as RemoteFacadeServer
import weblab.login.comm.server as LoginFacadeServer

import weblab.login.exc as LoginErrors

from test.unit.weblab.login.comm.test_manager import MockLogin

ZSI_PORT    = new_port()
JSON_PORT   = new_port()
XMLRPC_PORT = new_port()

class LoginIntegratingRemoteFacadeManagerZSI(unittest.TestCase):
    if LoginFacadeServer.ZSI_AVAILABLE:
        def setUp(self):
            self.configurationManager = ConfigurationManager.ConfigurationManager()
            self.configurationManager.append_module(configuration)

            self.configurationManager._set_value(configuration_doc.FACADE_TIMEOUT, 0.001)

            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_PORT, ZSI_PORT)
            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_SERVICE_NAME, '/weblab/soap/')
            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_LISTEN, '')

            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_JSON_PORT, JSON_PORT)
            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_JSON_LISTEN, '')

            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_XMLRPC_PORT, XMLRPC_PORT)
            self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_XMLRPC_LISTEN, '')


            self.mock_server      = MockLogin()
            self.rfs = LoginFacadeServer.LoginRemoteFacadeServer(self.mock_server, self.configurationManager)

        @uses_module(RemoteFacadeServer)
        def test_login(self):
            port = new_port()
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, port)
            self.rfs.start()
            try:
                wds = LoginWebLabDeustoSOAP("http://localhost:%s/weblab/soap/" % port)

                expected_sess_id = SessionId.SessionId("whatever")
                USERNAME = 'the username'
                PASSWORD = 'the password'
                MESSAGE  = 'my message'

                self.mock_server.return_values['login'] = expected_sess_id

                session = wds.login(USERNAME, PASSWORD)
                self.assertEquals(expected_sess_id.id, session.id)

                self.assertEquals(
                        USERNAME,
                        self.mock_server.arguments['login'][0]
                    )
                self.assertEquals(
                        PASSWORD,
                        self.mock_server.arguments['login'][1]
                    )

                self.mock_server.exceptions['login'] = LoginErrors.InvalidCredentialsError(MESSAGE)

                try:
                    wds.login(USERNAME, PASSWORD)
                    self.fail('exception expected')
                except ZSI.FaultException as e:
                    self.assertEquals(
                        LoginRFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE,
                        e.fault.code[1]
                    )
                    self.assertEquals(
                        MESSAGE,
                        e.fault.string
                    )
            finally:
                self.rfs.stop()

        @uses_module(RemoteFacadeServer)
        def test_extensible_login(self):
            port = new_port()
            self.configurationManager._set_value(self.rfs.FACADE_ZSI_PORT, port)
            self.rfs.start()
            try:
                wds = LoginWebLabDeustoSOAP("http://localhost:%s/weblab/soap/" % port)

                expected_sess_id = SessionId.SessionId("whatever")
                SYSTEM = 'facebook'
                CREDENTIALS = '(my credentials)'
                MESSAGE  = 'my message'

                self.mock_server.return_values['login_based_on_other_credentials'] = expected_sess_id

                session = wds.login_based_on_other_credentials(SYSTEM, CREDENTIALS)
                self.assertEquals(expected_sess_id.id, session.id)

                self.assertEquals(
                        SYSTEM,
                        self.mock_server.arguments['login_based_on_other_credentials'][0]
                    )
                self.assertEquals(
                        CREDENTIALS,
                        self.mock_server.arguments['login_based_on_other_credentials'][1]
                    )

                self.mock_server.exceptions['login_based_on_other_credentials'] = LoginErrors.InvalidCredentialsError(MESSAGE)

                try:
                    wds.login_based_on_other_credentials(SYSTEM, CREDENTIALS)
                    self.fail('exception expected')
                except ZSI.FaultException as e:
                    self.assertEquals(
                        LoginRFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE,
                        e.fault.code[1]
                    )
                    self.assertEquals(
                        MESSAGE,
                        e.fault.string
                    )
            finally:
                self.rfs.stop()

    else:
        print >> sys.stderr, "Optional module 'ZSI' not available (or maybe didn't run deploy.py?). Tests in weblab.login.comm.Integrating skipped"

class LoginIntegratingRemoteFacadeManagerJSON(unittest.TestCase):
    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)

        self.configurationManager._set_value(configuration_doc.FACADE_TIMEOUT, 0.001)

        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_PORT, ZSI_PORT)
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_SERVICE_NAME, '/weblab/soap/')
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_LISTEN, '')

        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_JSON_PORT, JSON_PORT)
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_JSON_LISTEN, '')

        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_XMLRPC_PORT, XMLRPC_PORT)
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_XMLRPC_LISTEN, '')


        self.mock_server      = MockLogin()
        self.rfs = LoginFacadeServer.LoginRemoteFacadeServer(self.mock_server, self.configurationManager)

    @uses_module(RemoteFacadeServer)
    def test_login(self):
        port = new_port()
        self.configurationManager._set_value(self.rfs.FACADE_JSON_PORT, port)
        self.rfs.start()
        try:
            client = WebLabDeustoClient('http://127.0.0.1:%s/weblab/' % port)

            expected_sess_id = SessionId.SessionId("whatever")
            USERNAME = 'the username'
            PASSWORD = 'the password'
            self.mock_server.return_values['login'] = expected_sess_id

            session = client.login(USERNAME, PASSWORD)
            self.assertEquals(expected_sess_id.id, session.id)

            self.assertEquals( USERNAME, self.mock_server.arguments['login'][0])
            self.assertEquals( PASSWORD, self.mock_server.arguments['login'][1])
        finally:
            self.rfs.stop()

def suite():
    return unittest.TestSuite((
                unittest.makeSuite(LoginIntegratingRemoteFacadeManagerZSI),
                unittest.makeSuite(LoginIntegratingRemoteFacadeManagerJSON)
            ))

if __name__ == '__main__':
    unittest.main()

