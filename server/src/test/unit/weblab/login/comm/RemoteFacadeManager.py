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
import sys
import unittest

try:
    import ZSI
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

import voodoo.sessions.SessionId as SessionId

import test.unit.configuration as configuration
import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.login.comm.manager as LoginFacadeManager
import weblab.comm.codes as RFCodes
import weblab.comm.RemoteFacadeManager as RFM
import weblab.login.comm.codes as LoginRFCodes

import weblab.login.exc as LoginExceptions
import weblab.exc as WebLabExceptions
import voodoo.gen.exceptions.exceptions as VoodooExceptions

class MockLogin(object):
    def __init__(self):
        super(MockLogin, self).__init__()
        self.arguments     = {}
        self.return_values = {}
        self.exceptions    = {}

    def login(self, username, password):
        self.arguments['login'] = (username, password)
        if self.exceptions.has_key('login'):
            raise self.exceptions['login']
        return self.return_values['login']

    def extensible_login(self, system, credentials):
        self.arguments['login_based_on_other_credentials'] = (system, credentials)
        if self.exceptions.has_key('login_based_on_other_credentials'):
            raise self.exceptions['login_based_on_other_credentials']
        return self.return_values['login_based_on_other_credentials']

class LoginFacadeManagerTestCase(unittest.TestCase):
    if ZSI_AVAILABLE:
        def setUp(self):

            self.cfg_manager   = ConfigurationManager.ConfigurationManager()
            self.cfg_manager.append_module(configuration)

            self.mock_login      = MockLogin()
            
            server_admin_mail = self.cfg_manager.get_value(RFM.SERVER_ADMIN_EMAIL, RFM.DEFAULT_SERVER_ADMIN_EMAIL)
            self.weblab_general_error_message = RFM.UNEXPECTED_ERROR_MESSAGE_TEMPLATE % server_admin_mail 

            self.rfm = LoginFacadeManager.LoginRemoteFacadeManagerZSI(
                    self.cfg_manager,
                    self.mock_login
                )

        def test_return_login(self):
            expected_sess_id  = SessionId.SessionId("whatever")
            expected_username = "whateverusername"
            expected_password = "whateverpassword"

            self.mock_login.return_values['login'] = expected_sess_id

            return_value = self.rfm.login(
                        expected_username,
                        expected_password
                    )
            self.assertEquals(expected_sess_id,  return_value)

        def test_return_extensible_login(self):
            expected_sess_id  = SessionId.SessionId("whatever")

            self.mock_login.return_values['login_based_on_other_credentials'] = expected_sess_id

            return_value = self.rfm.login_based_on_other_credentials(
                        "facebook",
                        "(my credentials)"
                    )
            self.assertEquals(expected_sess_id,  return_value)


        def _generate_real_mock_raising(self, method, exception, message):
            self.mock_login.exceptions[method] = exception(message)

        def _test_exception(self, method, args, exc_to_raise, exc_message, expected_code, expected_exc_message):
            self._generate_real_mock_raising(method, exc_to_raise, exc_message )

            try:
                getattr(self.rfm, method)(*args)
                self.fail('exception expected')
            except ZSI.Fault as e:
                self.assertEquals(expected_code, e.code)
                self.assertEquals(expected_exc_message, e.string)

        def _test_general_exceptions(self, method, *args):
            MESSAGE = "The exception message"
    
            # Production mode: A general error message is received
            self.cfg_manager._set_value(RFM.DEBUG_MODE, False)

            self._test_exception(method, args,  
                            LoginExceptions.LoginException, MESSAGE, 
                            'ZSI:' + LoginRFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

            self._test_exception(method, args,  
                            WebLabExceptions.WebLabException, MESSAGE, 
                            'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

            self._test_exception(method, args,  
                            VoodooExceptions.GeneratorException, MESSAGE, 
                            'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)

            self._test_exception(method, args,  
                            Exception, MESSAGE, 
                            'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, self.weblab_general_error_message)            
               
            # Debug mode: The error message is received
            self.cfg_manager._set_value(RFM.DEBUG_MODE, True)

            self._test_exception(method, args,  
                            LoginExceptions.LoginException, MESSAGE, 
                            'ZSI:' + LoginRFCodes.LOGIN_SERVER_EXCEPTION_CODE, MESSAGE)

            self._test_exception(method, args,  
                            WebLabExceptions.WebLabException, MESSAGE, 
                            'ZSI:' + RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE, MESSAGE)

            self._test_exception(method, args,  
                            VoodooExceptions.GeneratorException, MESSAGE, 
                            'ZSI:' + RFCodes.VOODOO_GENERAL_EXCEPTION_CODE, MESSAGE)

            self._test_exception(method, args,  
                            Exception, MESSAGE, 
                            'ZSI:' + RFCodes.PYTHON_GENERAL_EXCEPTION_CODE, MESSAGE)            

        def test_exception_login(self):
            expected_username = "whateverusername"
            expected_password = "whateverpassword"

            MESSAGE = 'whatever the message'

            self._test_exception('login', (expected_username, expected_password, ),  
                            LoginExceptions.InvalidCredentialsException, MESSAGE, 
                            'ZSI:' + LoginRFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE, MESSAGE)

                
            self._test_general_exceptions('login', expected_username, expected_password)

        def test_exception_extensible_login(self):
            MESSAGE = 'whatever the message'

            self._test_exception('login_based_on_other_credentials', ('facebook', '(my credentials)', ),  
                            LoginExceptions.InvalidCredentialsException, MESSAGE, 
                            'ZSI:' + LoginRFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE, MESSAGE)

                
            self._test_general_exceptions('login_based_on_other_credentials', 'facebook', '(my credentials)')

    else:
        print >> sys.stderr, "Optional library 'ZSI' not available. Tests in weblab.login.comm.RemoteFacadeManager skipped"
            
def suite():
    return unittest.makeSuite(LoginFacadeManagerTestCase)

if __name__ == '__main__':
    unittest.main()

