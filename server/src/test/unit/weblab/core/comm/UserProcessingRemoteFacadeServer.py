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
import unittest
import mocker

import sys
import time

import weblab.admin.bot.client as Client

import weblab.comm.RemoteFacadeServer as RemoteFacadeServer
import weblab.core.comm.user_server as UserProcessingFacadeServer
import weblab.data.Command as Command

import voodoo.configuration.ConfigurationManager as ConfigurationManager
import test.unit.configuration as configuration

import voodoo.sessions.SessionId as SessionId
from test.util.ModuleDisposer import uses_module

USERNAME         ='myusername'
PASSWORD         ='mypassword'
REAL_ID          ='this_is_the_real_id'
COMMAND          ='mycommand'
RESPONSE_COMMAND = 'myresponsecommand'


class WrappedRemoteFacadeServer(UserProcessingFacadeServer.UserProcessingRemoteFacadeServer):
    rfm_mock = None
    
    def _create_zsi_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock
    
    def _create_json_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock
    
    def _create_xmlrpc_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock
    
    
class UserProcessingRemoteFacadeServerTestCase(mocker.MockerTestCase):
    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)
        self.configurationManager._set_value(RemoteFacadeServer.RFS_TIMEOUT_NAME, 0.01)

        time.sleep( 0.01 * 5 )

        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_ZSI_PORT, 10223)
        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_ZSI_SERVICE_NAME, '/weblab/soap/')
        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_ZSI_LISTEN, '')

        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_PORT, 10224)
        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_LISTEN, '')

        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_XMLRPC_PORT, 10225)
        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_XMLRPC_LISTEN, '')

    if RemoteFacadeServer.ZSI_AVAILABLE:
        @uses_module(RemoteFacadeServer)
        def test_simple_use_zsi(self):
            response_command = Command.Command(RESPONSE_COMMAND)
            rfm_obj = self.mocker.mock()
            rfm_obj.send_command(mocker.ARGS)
            self.mocker.result( response_command )
            WrappedRemoteFacadeServer.rfm_mock = rfm_obj
            self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
            self.mocker.replay()            
            self.rfs.start()
            try:
                zsi_client = Client.BotZSI("http://localhost:10223/weblab/soap/", "http://localhost:10223/weblab/login/soap/")
                zsi_client.session_id = SessionId.SessionId(REAL_ID)
                response_command = zsi_client.do_send_command(Command.Command(COMMAND))
                self.assertEquals(response_command.commandstring, RESPONSE_COMMAND)
            finally:
                self.rfs.stop()
    else:
        print >> sys.stderr, "Optional library 'ZSI' not available. Skipped test in weblab.core.comm.RemoteFacadeServer"

    @uses_module(RemoteFacadeServer)
    def test_simple_use_json(self):
        session = {'id' : REAL_ID}
        command = {'commandstring' : COMMAND }
        response_command = {'commandstring' : RESPONSE_COMMAND }
        rfm_json = self.mocker.mock()
        rfm_json.send_command( session_id = session, command = command)
        self.mocker.result(response_command)
        WrappedRemoteFacadeServer.rfm_mock = rfm_json
        self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
        self.mocker.replay()
        self.rfs.start()
        try:
            json_client = Client.BotJSON("http://localhost:10224/weblab/json/", "http://localhost:10224/weblab/login/json/")
            json_client.session_id = SessionId.SessionId(REAL_ID)
            response_command = json_client.do_send_command(Command.Command(COMMAND))
            self.assertEquals(response_command.commandstring, RESPONSE_COMMAND)
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_simple_use_xmlrpc(self):
        session = {'id' : REAL_ID}
        command = {'commandstring' : COMMAND }
        response_command = {'commandstring' : RESPONSE_COMMAND }
        rfm_xmlrpc = self.mocker.mock()
        rfm_xmlrpc._dispatch('send_command', (session, command))
        self.mocker.result(response_command)
        WrappedRemoteFacadeServer.rfm_mock = rfm_xmlrpc
        self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
        self.mocker.replay()
        self.rfs.start()
        try:
            xmlrpc_client = Client.BotXMLRPC("http://localhost:10225/weblab/xmlrpc/", "http://localhost:10225/weblab/login/xmlrpc")
            xmlrpc_client.session_id = SessionId.SessionId(REAL_ID)
            response_command = xmlrpc_client.do_send_command(Command.Command(COMMAND))
            self.assertEquals(response_command.commandstring, RESPONSE_COMMAND)
        finally:
            self.rfs.stop()



def suite():
    return unittest.makeSuite(UserProcessingRemoteFacadeServerTestCase)

if __name__ == '__main__':
    unittest.main()

