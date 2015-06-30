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

from test.unit.weblab.proxy import fake_time
from voodoo.gen import CoordAddress
import weblab.proxy.session_handler as ProxySessionHandler
import mocker
import os
import test.unit.configuration as configuration_module
import time
import unittest
import voodoo.configuration as ConfigurationManager
import weblab.experiment.util as ExperimentUtil
from weblab.data.command import Command
from weblab.translator.translators import StoresEverythingTranslator


class ProxySessionHandlerTestCase(mocker.MockerTestCase):

    def setUp(self):
        self._cfg_manager = ConfigurationManager.ConfigurationManager()
        self._cfg_manager.append_module(configuration_module)

        self.ANY_COORD_ADDR = CoordAddress.translate('myserver:myprocess@mymachine')

        self._clean_up_files_stored_dir()

    def _clean_up_files_stored_dir(self):
        path = self._cfg_manager.get_value('proxy_store_students_programs_path')
        if not os.path.isdir(path):
            raise RuntimeError("The provided proxy_store_students_programs_path is not a directory: %s" % path)
        for i in os.listdir(path):
            if not os.path.isdir(os.sep.join([path, i])) and not i.endswith('.hidden'):
                os.remove(os.sep.join([path, i]))

    def _create_proxy_session_handler(self, session={}, laboratory=None, translator=None, time_mock=None):
        if translator is None:
            translator = StoresEverythingTranslator(None, None, self._cfg_manager)
        psh = ProxySessionHandler.ProxySessionHandler(session, laboratory, translator, self._cfg_manager, None, None)
        if time_mock is not None:
            psh._time = time_mock
        return psh

    #===========================================================================
    # _store_file()
    #===========================================================================

    def _test_store_file(self, file_content):
        FILE_PATH = self._cfg_manager.get_value('proxy_store_students_programs_path')
        FILE_CONTENT = ExperimentUtil.serialize(file_content)
        fake_time.TIME_TO_RETURN = 1289548551.2617509 # 2010_11_12___07_55_51

        proxy = self._create_proxy_session_handler(time_mock=fake_time)
        path, hash = proxy._store_file(Command(FILE_CONTENT), "student1", "my_session_id")
        self.assertEquals(
            '2010_11_12___07_55_51_261_student1_my_session_id',
            path
        )
        self.assertTrue(
            os.path.exists('%s%s%s' % (FILE_PATH, os.sep, path))
        )
        self.assertEquals(
            '{sha}14b69e2393ace3feb980510e59dc8a1fc467575a', # sha of 'AAAHuuuuuuuuge file!'
            hash
        )

    def test_store_file_string(self):
        self._test_store_file('Huuuuuuuuge file!')

    def test_store_file_unicode(self):
        self._test_store_file(u'Huuuuuuuuge file!')

    #===================================================================
    # poll()
    #===================================================================

    def test_poll_when_polling(self):
        session = {'session_polling': (time.time() - 1, ProxySessionHandler.ProxySessionHandler.EXPIRATION_TIME_NOT_SET)}
        psh = self._create_proxy_session_handler(session=session)

        timestamp_before = psh._session['session_polling'][0]
        psh.poll()
        timestamp_after = psh._session['session_polling'][0]
        self.assertTrue(timestamp_after > timestamp_before)

    #===========================================================================
    # is_expired()
    #===========================================================================

    def test_is_expired_when_not_polling(self):
        session = {'trans_session_id': 'my_trans_session_id'}
        psh = self._create_proxy_session_handler(session=session)
        self.assertEquals("Y <still-polling>", psh.is_expired())

    def test_is_expired_when_polling_but_time_expired_without_expiration_time_set(self):
        session = {'trans_session_id': 'my_trans_session_id'}
        psh = self._create_proxy_session_handler(session=session, time_mock=fake_time)

        fake_time.TIME_TO_RETURN = time.time()
        psh.enable_access()
        self.assertEquals("N", psh.is_expired())

        self._cfg_manager._set_value(ProxySessionHandler.EXPERIMENT_POLL_TIME, 30)
        fake_time.TIME_TO_RETURN = fake_time.TIME_TO_RETURN + 31
        self.assertEquals("Y <poll-time-expired>", psh.is_expired())

    def test_is_expired_when_polling_but_time_expired_due_to_expiration_time(self):
        session = {'trans_session_id': 'my_trans_session_id'}
        psh = self._create_proxy_session_handler(session=session, time_mock=fake_time)

        fake_time.TIME_TO_RETURN = time.time()
        psh.enable_access()
        self.assertEquals("N", psh.is_expired())

        self._cfg_manager._set_value(ProxySessionHandler.EXPERIMENT_POLL_TIME, 30)
        psh._renew_expiration_time(fake_time.TIME_TO_RETURN + 10)
        fake_time.TIME_TO_RETURN = fake_time.TIME_TO_RETURN + 11
        self.assertEquals("Y <expiration-time-expired>", psh.is_expired())

    def tearDown(self):
        self._clean_up_files_stored_dir()


def suite():
    return unittest.TestSuite(
            (
                unittest.makeSuite(ProxySessionHandlerTestCase)
            )
        )

if __name__ == '__main__':
    unittest.main()
