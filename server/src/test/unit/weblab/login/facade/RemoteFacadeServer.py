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

import sys
import unittest
import mocker

import time

import weblab.admin.bot.Client as Client

import weblab.facade.RemoteFacadeServer as RemoteFacadeServer
import weblab.login.facade.LoginFacadeServer as LoginFacadeServer

import voodoo.configuration.ConfigurationManager as ConfigurationManager
import test.unit.configuration as configuration

import voodoo.sessions.SessionId as SessionId
from test.util.ModuleDisposer import uses_module

USERNAME         ='myusername'
PASSWORD         ='mypassword'
REAL_ID          ='this_is_the_real_id'


class WrappedRemoteFacadeServer(LoginFacadeServer.LoginRemoteFacadeServer):
    rfm_mock = None
    
    def _create_zsi_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock
    
    def _create_json_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock
    
    def _create_xmlrpc_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock


class LoginRemoteFacadeServerTestCase(mocker.MockerTestCase):

    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)
        self.configurationManager._set_value(RemoteFacadeServer.RFS_TIMEOUT_NAME, 0.01)

        time.sleep( 0.01 * 5 )

        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_PORT, 10123)
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_SERVICE_NAME, '/weblab/login/soap/')
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_ZSI_LISTEN, '')

        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_JSON_PORT, 10124)
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_JSON_LISTEN, '')

        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_XMLRPC_PORT, 10125)
        self.configurationManager._set_value(LoginFacadeServer.LOGIN_FACADE_XMLRPC_LISTEN, '')

    if RemoteFacadeServer.ZSI_AVAILABLE:

        @uses_module(RemoteFacadeServer)
        def test_simple_use_zsi(self):
            session_to_return = SessionId.SessionId(REAL_ID)
            rfm_obj = self.mocker.mock()
            rfm_obj.login(USERNAME, PASSWORD)
            self.mocker.result(session_to_return)
            WrappedRemoteFacadeServer.rfm_mock = rfm_obj
            self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
            self.mocker.replay()
            self.rfs.start()
            try:
                zsi_client = Client.BotZSI("http://localhost:10123/weblab/soap/", "http://localhost:10123/weblab/login/soap/")
                session = zsi_client.do_login(USERNAME, PASSWORD)
                self.assertEquals(session.id, REAL_ID)
            finally:
                self.rfs.stop()
    else:
        
        print >> sys.stderr, "Optional library 'ZSI' not available. Skipping test int weblab.login.facade.RemoteFacadeServer"

    @uses_module(RemoteFacadeServer)
    def test_simple_use_json(self):
        session_to_return = {'id' : REAL_ID}
        rfm_json = self.mocker.mock()
        rfm_json.login( username = unicode(USERNAME), password = unicode(PASSWORD))
        self.mocker.result(session_to_return)
        WrappedRemoteFacadeServer.rfm_mock = rfm_json
        self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
        self.mocker.replay()
        self.rfs.start()
        try:
            json_client = Client.BotJSON("http://localhost:10124/weblab/json/", "http://localhost:10124/weblab/login/json/")
            session = json_client.do_login(USERNAME, PASSWORD)
            self.assertEquals(session.id, REAL_ID)
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_simple_use_xmlrpc(self):
        session_to_return = {'id' : REAL_ID}
        rfm_xmlrpc = self.mocker.mock()
        rfm_xmlrpc._dispatch('login', (USERNAME, PASSWORD))
        self.mocker.result(session_to_return)
        WrappedRemoteFacadeServer.rfm_mock = rfm_xmlrpc
        self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
        self.mocker.replay()
        self.rfs.start()
        try:
            xmlrpc_client = Client.BotXMLRPC("http://localhost:10125/weblab/xmlrpc/", "http://localhost:10125/weblab/login/xmlrpc/")
            session = xmlrpc_client.do_login(USERNAME, PASSWORD)
            self.assertEquals(session.id, REAL_ID)
        finally:
            self.rfs.stop()


def suite():
    return unittest.makeSuite(LoginRemoteFacadeServerTestCase)

if __name__ == '__main__':
    unittest.main()

