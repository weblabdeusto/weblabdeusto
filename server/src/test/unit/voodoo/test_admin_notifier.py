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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import unittest
import mocker

import weblab.configuration_doc as configuration_doc

import test.unit.configuration as configuration_module

import voodoo.admin_notifier as AdminNotifier
import voodoo.configuration as ConfigurationManager
import voodoo.configuration as ConfigurationErrors

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
        if key in self._configuration:
            return self._configuration[key]
        elif other != 'lalala':
            return other
        else:
            raise ConfigurationErrors.KeyNotFoundError(
                'lalalaa',
                'lelele'
            )
    def get_doc_value(self, key):
        default = configuration_doc.variables[key].default
        if default == configuration_doc.NO_DEFAULT:
            return self.get_value(key)
        return self.get_value(key, default)

class AdminNotifierTestCase(mocker.MockerTestCase):

    def setUp(self):
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
        cfg_manager._set_value('mail_notification_enabled', True)
        self.smtp_mock = self.mocker.mock()
        self.smtp_mock.starttls()
        self.smtp_mock.helo('weblab.deusto.es')
        self.smtp_mock.sendmail(mocker.ARGS)
        self.smtp_mock.close()
        notifier = AdminNotifierFake(cfg_manager, 'rigel.deusto.es', self.smtp_mock)

        self.mocker.replay()
        result = notifier.notify('message')
        self.assertEquals(0, result)
        self.assertTrue(notifier.verify())

    def test_without_enough_configuration(self):
        self.default_config.pop(configuration_doc.MAIL_SERVER_HOST)
        cfg_manager= ConfigurationManagerFake(self.default_config)
        self.smtp_mock = self.mocker.mock()
        notifier = AdminNotifierFake(cfg_manager, 'rigel.deusto.es', self.smtp_mock)

        self.mocker.replay()
        result = notifier.notify('message')
        self.assertEquals(-1, result)

    def test_with_wrong_configuration(self):
        self.default_config['mail_server_helo'] = 'lalala'
        cfg_manager= ConfigurationManagerFake(self.default_config)
        self.smtp_mock = self.mocker.mock()
        self.smtp_mock.starttls()
        self.smtp_mock.helo('lalala')
        self.smtp_mock.close()
        notifier = AdminNotifierFake(cfg_manager, 'rigel.deusto.es', self.smtp_mock)

        self.mocker.replay()
        result = notifier.notify('message')
        self.assertEquals(-2, result)


def real_test():
    cfg_manager= ConfigurationManager.ConfigurationManager()
    cfg_manager.append_module(configuration_module)

    notifier = AdminNotifier.AdminNotifier(cfg_manager)
    notifier.notify('message')

    print("Verify in your e-mail address :-D")


def suite():
    return unittest.makeSuite(AdminNotifierTestCase)

if __name__ == '__main__':
    unittest.main()

