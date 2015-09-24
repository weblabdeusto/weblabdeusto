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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

from weblab.translator.translators import StoresEverythingExceptForFilesTranslator
import test.unit.configuration as configuration_module
import unittest
import voodoo.configuration as ConfigurationManager


class StoresEverythingExceptForFilesTranslatorTestCase(unittest.TestCase):

    def setUp(self):
        self._cfg_manager = ConfigurationManager.ConfigurationManager()
        self._cfg_manager.append_module(configuration_module)
        self.translator = StoresEverythingExceptForFilesTranslator(None, None, self._cfg_manager)

    def test(self):
        self.assertEquals(
            None,
            self.translator.do_on_start('session_id')
        )

        self.assertEquals(
            'command',
            self.translator.do_before_send_command('session_id', 'command')
        )

        self.assertEquals(
            'response',
            self.translator.do_after_send_command('session_id', 'response')
        )

        self.assertEquals(
            None,
            self.translator.do_before_send_file('session_id', 'file')
        )

        self.assertEquals(
            None,
            self.translator.do_after_send_file('session_id', 'response')
        )

        self.assertEquals(
            None,
            self.translator.do_on_finish('session_id')
        )


def suite():
    return unittest.makeSuite(StoresEverythingExceptForFilesTranslatorTestCase)

if __name__ == '__main__':
    unittest.main()
