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
import unittest
import mocker

import sys
import time

from test.util.ports import new as new_port

import weblab.configuration_doc as configuration_doc

import weblab.admin.bot.client as Client

import weblab.comm.server as RemoteFacadeServer
import weblab.core.comm.user_server as UserProcessingFacadeServer
import weblab.data.command as Command

import voodoo.configuration as ConfigurationManager
import test.unit.configuration as configuration

import voodoo.sessions.session_id as SessionId
from test.util.module_disposer import uses_module

USERNAME         ='myusername'
PASSWORD         ='mypassword'
REAL_ID          ='this_is_the_real_id'
COMMAND          ='mycommand'
RESPONSE_COMMAND = 'myresponsecommand'


class WrappedRemoteFacadeServer(UserProcessingFacadeServer.UserProcessingRemoteFacadeServer):
    rfm_mock = None
    
    def _create_json_remote_facade_manager(self, *args, **kwargs):
        return self.rfm_mock
    
JSON_PORT   = new_port()
    
class UserProcessingRemoteFacadeServerTestCase(mocker.MockerTestCase):
    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)
        self.configurationManager._set_value(configuration_doc.FACADE_TIMEOUT, 0.01)

        time.sleep( 0.01 * 5 )

        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_PORT, JSON_PORT)
        self.configurationManager._set_value(UserProcessingFacadeServer.USER_PROCESSING_FACADE_JSON_LISTEN, '')

    @uses_module(RemoteFacadeServer)
    def test_simple_use_json(self):
        session = {'id' : REAL_ID}
        command = {'commandstring' : COMMAND }
        response_command = {'commandstring' : RESPONSE_COMMAND }
        rfm_json = self.mocker.mock()
        rfm_json.send_command( reservation_id = session, command = command)
        self.mocker.result(response_command)
        WrappedRemoteFacadeServer.rfm_mock = rfm_json
        self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
        self.mocker.replay()
        self.rfs.start()
        try:
            json_client = Client.BotJSON("http://localhost:%s/weblab/json/" % JSON_PORT, "http://localhost:%s/weblab/login/json/" % JSON_PORT)
            json_client.reservation_id = SessionId.SessionId(REAL_ID)
            response_command = json_client.do_send_command(Command.Command(COMMAND))
            self.assertEquals(response_command.commandstring, RESPONSE_COMMAND)
        finally:
            self.rfs.stop()

def suite():
    return unittest.makeSuite(UserProcessingRemoteFacadeServerTestCase)

if __name__ == '__main__':
    unittest.main()

