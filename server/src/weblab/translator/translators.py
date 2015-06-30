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

from voodoo import log
from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
from voodoo.override import Override
from weblab.data import server_type as ServerType
import weblab.translator.translator as translator


class StoresNothingTranslator(translator.Translator):

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_on_start(self, session_id):
        super(StoresNothingTranslator, self).do_on_start(session_id)

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_command(self, session_id, command):
        return None

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_command(self, session_id, response):
        return None

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_file(self, session_id, file):
        return None

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_file(self, session_id, response):
        return None

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_on_finish(self, session_id):
        super(StoresNothingTranslator, self).do_on_finish(session_id)


class StoresEverythingTranslator(translator.Translator):

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_on_start(self, session_id):
        super(StoresEverythingTranslator, self).do_on_start(session_id)

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_command(self, session_id, command):
        return command

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_command(self, session_id, response):
        return response

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_file(self, session_id, file):
        return file

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_file(self, session_id, response):
        return response

    @Override(translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_on_finish(self, session_id):
        super(StoresEverythingTranslator, self).do_on_finish(session_id)


class StoresEverythingExceptForFilesTranslator(StoresEverythingTranslator):

    @Override(StoresEverythingTranslator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_file(self, session_id, file):
        return None

    @Override(StoresEverythingTranslator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_file(self, session_id, response):
        return None
