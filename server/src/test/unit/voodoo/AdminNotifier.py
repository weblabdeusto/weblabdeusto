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
import pmock

import test.unit.configuration as configuration_module

import voodoo.AdminNotifier as AdminNotifier
import voodoo.configuration.ConfigurationManager as ConfigurationManager
import voodoo.exceptions.configuration.ConfigurationExceptions as ConfigurationExceptions

class AdminNotifierFake(AdminNotifier.AdminNotifier):
    def __init__(self, configuration, expected, smtp_mock):
        super(AdminNotifierFake, self).__init__(configuration)
        self.verification = False
        self.expected     = expected
        self.smtp_mock    = smtp_mock

    def _create_mailer(self, mailer_server):
        self.verification = False
        if mailer_server == self.expected:
            self.verification = True
        return self.smtp_mock

    def verify(self):
        return self.verification

class ConfigurationManagerFake(object):
    def __init__(self, configuration):
        super(ConfigurationManagerFake,self).__init__()
        self._configuration = configuration
    def get_value(self, key, other = 'lalala'):
        if self._configuration.has_key(key):
            return self._configuration[key]
        elif other != 'lalala':
            return other
        else:
            raise ConfigurationExceptions.KeyNotFoundException(
                'lalalaa',
                'lelele'
            )

class AdminNotifierTestCase(unittest.TestCase):
    def setUp(self):
        self.smtp_mock   = pmock.Mock()
        self.smtp_mock.expects(pmock.once()).starttls()
        self.smtp_mock.expects(pmock.once()).helo(
                pmock.eq('weblab.deusto.es')
            ).after('starttls')
        self.smtp_mock.expects(pmock.once()).method('sendmail')
        self.smtp_mock.expects(pmock.once()).close().after('sendmail')
        self.default_config = dict(
            server_hostaddress        = 'weblab.deusto.es',
            server_admin              = 'weblab@deusto.es',
            mail_notification_enabled = True,
            mail_server_host          = 'rigel.deusto.es',
            mail_server_use_tls       = 'yes',
            mail_server_helo          = 'weblab.deusto.es',
            mail_notification_sender  = 'weblab@deusto.es'
        )
    
    def test_with_real_configuration(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)
        cfg_manager._set_value('mail_notification_enabled',True)

        
        notifier    = AdminNotifierFake(
                    cfg_manager,
                    'rigel.deusto.es',
                    self.smtp_mock
                )

        result = notifier.notify('message')
        self.assertEquals(
                0,
                result
            )

        self.assertTrue(
                notifier.verify()
            )
        self.smtp_mock.verify()

    def test_without_enough_configuration(self):
        self.default_config.pop('server_hostaddress')
        cfg_manager= ConfigurationManagerFake(
                self.default_config
            )
        
        notifier    = AdminNotifierFake(
                    cfg_manager,
                    'rigel.deusto.es',
                    self.smtp_mock
                )

        result = notifier.notify('message')
        self.assertEquals(
                -1,
                result
            )

    def test_with_wrong_configuration(self):
        self.default_config['mail_server_helo'] = 'lalala'
        cfg_manager= ConfigurationManagerFake(
                self.default_config
            )
        
        notifier    = AdminNotifierFake(
                    cfg_manager,
                    'rigel.deusto.es',
                    self.smtp_mock
                )

        result = notifier.notify('message')
        self.assertEquals(
                -2,
                result
            )

def real_test():
    cfg_manager= ConfigurationManager.ConfigurationManager()
    cfg_manager.append_module(configuration_module)

    notifier    = AdminNotifier.AdminNotifier(cfg_manager)
    result = notifier.notify('message')
    
    print "Verify in your e-mail address :-D"


def suite():
    return unittest.makeSuite(AdminNotifierTestCase)

if __name__ == '__main__':
    unittest.main()

