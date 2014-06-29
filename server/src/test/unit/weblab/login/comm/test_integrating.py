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

JSON_PORT   = new_port()
XMLRPC_PORT = new_port()

class MockLogin(object):
    def __init__(self):
        super(MockLogin, self).__init__()
        self.arguments     = {}
        self.return_values = {}
        self.exceptions    = {}

    def login(self, username, password):
        self.arguments['login'] = (username, password)
        if 'login' in self.exceptions:
            raise self.exceptions['login']
        return self.return_values['login']

    def extensible_login(self, system, credentials):
        self.arguments['login_based_on_other_credentials'] = (system, credentials)
        if 'login_based_on_other_credentials' in self.exceptions:
            raise self.exceptions['login_based_on_other_credentials']
        return self.return_values['login_based_on_other_credentials']

class LoginIntegratingRemoteFacadeManagerJSON(unittest.TestCase):
    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)

        self.configurationManager._set_value(configuration_doc.FACADE_TIMEOUT, 0.001)

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
                unittest.makeSuite(LoginIntegratingRemoteFacadeManagerJSON)
            ))

if __name__ == '__main__':
    unittest.main()

