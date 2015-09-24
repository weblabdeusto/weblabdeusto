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

from test.unit.weblab.proxy import adds_triple_translator, fake_time
from voodoo.sessions import exc as SessionErrors
from voodoo.gen import CoordAddress
from voodoo.sessions import session_id as SessionId
from weblab.data import server_type as ServerType
from weblab.data.command import Command
import weblab.lab.exc as LaboratoryErrors
import weblab.proxy.exc as ProxyErrors
from weblab.proxy import server as ProxyServer
from weblab.translator.translators import StoresNothingTranslator, StoresEverythingTranslator
import mocker
import test.unit.configuration as configuration_module
import unittest
import voodoo.configuration as ConfigurationManager
import weblab.experiment.util as ExperimentUtil
import weblab.methods as weblab_methods


class CreatingProxyServerTestCase(mocker.MockerTestCase):

    def setUp(self):
        self._cfg_manager = ConfigurationManager.ConfigurationManager()
        self._cfg_manager.append_module(configuration_module)

    def test_invalid_session_type_name(self):
        self._cfg_manager._set_value(ProxyServer.WEBLAB_PROXY_SERVER_SESSION_TYPE, "this_will_never_be_a_valid_session_type")
        self.assertRaises(
            ProxyErrors.NotASessionTypeError,
            ProxyServer.ProxyServer, None, None, self._cfg_manager
        )

    def test_invalid_default_translator_klazz_name(self):
        self._cfg_manager._set_value(ProxyServer.WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME, "ThisWillNeverBeAValidDefaultTranslatorKlazzName")
        self.assertRaises(
            ProxyErrors.InvalidDefaultTranslatorNameError,
            ProxyServer.ProxyServer, None, None, self._cfg_manager
        )


class UsingProxyServerTestCase(mocker.MockerTestCase):

    def setUp(self):
        self._cfg_manager = ConfigurationManager.ConfigurationManager()
        self._cfg_manager.append_module(configuration_module)

        self.RESERVATION_ID = "my_reservation_id"
        self.RESERVATION_SESS_ID = SessionId.SessionId(self.RESERVATION_ID)
        self.LAB_SESS_ID = "my_lab_sess_id"
        self.ANY_COORD_ADDR = CoordAddress.translate('translator:myprocess@mymachine')
        self.LAB_COORD_ADDR = CoordAddress.translate('laboratory:myprocess@mymachine')

    def _create_proxy(self, laboratories=None, translators=None, time_mock=None):
        clients = {}
        if laboratories:
            clients['laboratory:myprocess@mymachine'] = laboratories
        if translators:
            clients['translator:myprocess@mymachine'] = translators
        locator = FakeLocator(clients)
        proxy = ProxyServer.ProxyServer(None, locator, self._cfg_manager)
        if time_mock is not None:
            proxy._time = time_mock
        return proxy

    def _create_custom_translator(self, translator_klazz):
        locator = FakeLocator()
        return translator_klazz(self.ANY_COORD_ADDR, locator, self._cfg_manager)

    #===========================================================================
    # _find_translator()
    #===========================================================================

    def test_find_translator_being_a_suitable_translator_available(self):
        translator = self._create_custom_translator(StoresNothingTranslator)
        proxy = self._create_proxy(translators=translator)

        found_translator, is_default = proxy._find_translator("whichever experiment_id, because FakeLocator will find it ;-)")
        self.assertFalse(is_default)
        self.assertEquals(translator, found_translator)

    def test_find_translator_not_being_any_suitable_translator_available_so_using_an_explicit_default_one(self):
        self._cfg_manager._set_value(ProxyServer.WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME, "StoresNothingTranslator")
        proxy = self._create_proxy()

        found_translator, is_default = proxy._find_translator("whichever experiment_id, because FakeLocator won't find it...")
        self.assertEquals(StoresNothingTranslator, found_translator.__class__)
        self.assertTrue(is_default)

    def test_find_translator_not_being_any_suitable_translator_available_so_using_the_implicit_default_one(self):
        proxy = self._create_proxy()

        found_translator, is_default = proxy._find_translator("whichever experiment_id, because FakeLocator won't find it...")
        self.assertEquals(StoresEverythingTranslator, found_translator.__class__)
        self.assertTrue(is_default)

    #===========================================================================
    # Using the API: enable_access(), send_command(), send_file(), are_expired(), disable_access(), retrieve_results()
    #===========================================================================

    def _test_command_sent(self, command_sent, expected_command, expected_response):
        self.assertEquals(expected_command, command_sent.command.commandstring)
        self.assertEquals(expected_response, command_sent.response.commandstring)
        self.assertTrue(isinstance(command_sent.timestamp_before, float))
        self.assertTrue(isinstance(command_sent.timestamp_after, float))
        self.assertTrue(command_sent.timestamp_after >= command_sent.timestamp_before)

    def _test_file_sent(self, file_sent, expected_file_info, expected_response):
        self.assertEquals(expected_file_info, file_sent.file_info)
        self.assertEquals(expected_response, file_sent.response.commandstring)
        self.assertTrue(isinstance(file_sent.timestamp_before, float))
        self.assertTrue(isinstance(file_sent.timestamp_after, float))
        self.assertTrue(file_sent.timestamp_after >= file_sent.timestamp_before)

    def _test_happy_path(self, translator_name):
        FILE_CONTENT = ExperimentUtil.serialize('Huuuuuuuuge file!')
        FILE_INFO = "My file's description"

        self._cfg_manager._set_value(ProxyServer.WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME, translator_name)
        fake_time.TIME_TO_RETURN = 1289548551.2617509 # 2010_11_12___07_55_51

        laboratory = self.mocker.mock()
        laboratory.send_command(self.LAB_SESS_ID, Command('Do this!'))
        self.mocker.result(Command('Done!'))
        laboratory.send_file(self.LAB_SESS_ID, Command(FILE_CONTENT), FILE_INFO)
        self.mocker.result(Command('File received!'))

        self.mocker.replay()
        proxy = self._create_proxy(laboratories=laboratory, time_mock=fake_time)

        proxy.do_enable_access(self.RESERVATION_ID, "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)

        command_response = proxy.send_command(self.RESERVATION_SESS_ID, Command('Do this!'))
        self.assertEquals(Command('Done!'), command_response)

        file_response = proxy.send_file(self.RESERVATION_SESS_ID, Command(FILE_CONTENT), FILE_INFO)
        self.assertEquals(Command('File received!'), file_response)

        proxy.do_disable_access(self.RESERVATION_ID)

        commands, files = proxy.do_retrieve_results(self.RESERVATION_ID)
        return commands, files

    def test_happy_path_using_a_translator_that_stores(self):
        # Since this is not a really default Translator, we have to make it available for the test
        ProxyServer.DEFAULT_TRANSLATORS['AddsATrippleAAtTheBeginingTranslator'] = adds_triple_translator.AddsATrippleAAtTheBeginingTranslator

        commands, files = self._test_happy_path("AddsATrippleAAtTheBeginingTranslator")

        self.assertEquals(2, len(commands))
        self._test_command_sent(
            commands[0],
            'AAADo this!', 'AAADone!'
        )
        self._test_command_sent(
            commands[1],
            'on_finish', 'on_start before_send_command after_send_command before_send_file after_send_file do_on_finish '
        )

        self.assertEquals(1, len(files))
        self._test_file_sent(
            files[0],
            "My file's description",
            'AAAFile received!'
        )

    def test_happy_path_using_a_translator_that_does_not_store(self):
        commands, files = self._test_happy_path("StoresNothingTranslator")
        self.assertEquals(0, len(commands))
        self.assertEquals(0, len(files))

    def test_doing_anything_before_enabling(self):
        proxy = self._create_proxy()

        # Can't disable access, of course
        self.assertRaises(
            ProxyErrors.InvalidReservationIdError,
            proxy.do_disable_access,
            self.RESERVATION_ID
        )

        # Can't check if the user is online
        expirations = proxy.do_are_expired([self.RESERVATION_ID])
        self.assertEquals("Y <sessionid-not-found>", expirations[0])

        # Can't retrieve results
        self.assertRaises(
            SessionErrors.SessionNotFoundError,
            proxy.do_retrieve_results,
            self.RESERVATION_ID
        )

        # Can't poll
        self.assertRaises(
            ProxyErrors.InvalidReservationIdError,
            proxy.poll,
            self.RESERVATION_SESS_ID
        )

        # Can't work with the experiment
        self.assertRaises(
            ProxyErrors.InvalidReservationIdError,
            proxy.send_command,
            self.RESERVATION_SESS_ID, 'command'
        )
        self.assertRaises(
            ProxyErrors.InvalidReservationIdError,
            proxy.send_file,
            self.RESERVATION_SESS_ID, 'file'
        )

    def test_doing_anything_after_disabling(self):
        return #TODO
        proxy = self._create_proxy()
        proxy.do_enable_access(self.RESERVATION_ID, "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)
        proxy.do_disable_access(self.RESERVATION_ID)

        # Can't poll
        self.assertRaises(
            ProxyErrors.AccessDisabledError,
            proxy.poll,
            self.RESERVATION_SESS_ID
        )

        # Can't work with the experiment
        self.assertRaises(
            ProxyErrors.AccessDisabledError,
            proxy.send_command,
            self.RESERVATION_SESS_ID, 'command'
        )
        self.assertRaises(
            ProxyErrors.AccessDisabledError,
            proxy.send_file,
            self.RESERVATION_SESS_ID, 'file'
        )

        # Can't disable access again, of course
        self.assertRaises(
            ProxyErrors.AccessDisabledError,
            proxy.do_disable_access,
            self.RESERVATION_ID
        )

        # CAN retrieve results!
        proxy.do_retrieve_results(self.RESERVATION_ID)

    def test_failed_to_send_command(self):
        laboratory = self.mocker.mock()
        laboratory.send_command(self.LAB_SESS_ID, 'command')
        self.mocker.throw(LaboratoryErrors.FailedToSendCommandError)

        self.mocker.replay()
        proxy = self._create_proxy(laboratories=laboratory)

        proxy.do_enable_access(self.RESERVATION_ID, "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)

        self.assertRaises(
            ProxyErrors.FailedToSendCommandError,
            proxy.send_command,
            self.RESERVATION_SESS_ID, 'command'
        )

        # Access becomes disabled
        self.assertRaises(
            ProxyErrors.AccessDisabledError,
            proxy.send_command,
            self.RESERVATION_SESS_ID, 'command'
        )

    def test_failed_to_send_file(self):
        laboratory = self.mocker.mock()
        laboratory.send_file(self.LAB_SESS_ID, 'file', 'info')
        self.mocker.throw(LaboratoryErrors.FailedToSendFileError)

        self.mocker.replay()
        proxy = self._create_proxy(laboratories=laboratory)

        proxy.do_enable_access(self.RESERVATION_ID, "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)

        self.assertRaises(
            ProxyErrors.FailedToSendFileError,
            proxy.send_file,
            self.RESERVATION_SESS_ID, 'file', 'info'
        )

        # Access becomes disabled
        self.assertRaises(
            ProxyErrors.AccessDisabledError,
            proxy.send_file,
            self.RESERVATION_SESS_ID, 'file', 'info'
        )

    def test_invalid_laboratory_session_id_when_sending_a_command(self):
        laboratory = self.mocker.mock()
        laboratory.send_command(self.LAB_SESS_ID, 'command')
        self.mocker.throw(LaboratoryErrors.SessionNotFoundInLaboratoryServerError)

        self.mocker.replay()
        proxy = self._create_proxy(laboratories=laboratory)

        proxy.do_enable_access(self.RESERVATION_ID, "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)

        self.assertRaises(
            ProxyErrors.NoCurrentReservationError,
            proxy.send_command,
            self.RESERVATION_SESS_ID, 'command'
        )

    def test_invalid_laboratory_session_id_when_sending_a_file(self):
        laboratory = self.mocker.mock()
        laboratory.send_file(self.LAB_SESS_ID, 'file', 'info')
        self.mocker.throw(LaboratoryErrors.SessionNotFoundInLaboratoryServerError)

        self.mocker.replay()
        proxy = self._create_proxy(laboratories=laboratory)

        proxy.do_enable_access(self.RESERVATION_ID, "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)

        self.assertRaises(
            ProxyErrors.NoCurrentReservationError,
            proxy.send_file,
            self.RESERVATION_SESS_ID, 'file', 'info'
        )

    def test_are_expired(self):
        return #TODO
        proxy = self._create_proxy()
        session_ids = ["reservation_id1", "reservation_id2", "reservation_id3"]
        proxy.do_enable_access(session_ids[0], "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)
        proxy.do_enable_access(session_ids[1], "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)
        proxy.do_enable_access("invalid-reservation-id", "ud-fpga@FPGA experiments", "student1", self.LAB_COORD_ADDR, self.LAB_SESS_ID)

        expirations = proxy.do_are_expired(session_ids)
        self.assertEquals(3, len(expirations))
        self.assertEquals("N", expirations[0])
        self.assertEquals("N", expirations[1])
        self.assertEquals("Y <sessionid-not-found>", expirations[2])


class FakeLocator(object):

    def __init__(self, clients={}):
        self.clients = clients

    def __getitem__(self, coord_address):
        return self.clients[coord_address]

    def find_by_type(self, server_type):
        for client in self.clients:
            if client.lower().startswith(server_type.lower()):
                return [client]
        return []

def suite():
    return unittest.TestSuite(
            (
                unittest.makeSuite(CreatingProxyServerTestCase),
                unittest.makeSuite(UsingProxyServerTestCase)
            )
        )

if __name__ == '__main__':
    unittest.main()
