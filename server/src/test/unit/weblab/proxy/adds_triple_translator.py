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
from voodoo.sessions.checker import check_session
from weblab.data import server_type as ServerType
from weblab.data.command import Command
import weblab.translator.exc as TranslatorErrors
import weblab.translator.translator as Translator
import weblab.experiment.util as ExperimentUtil


check_session_params = (
        TranslatorErrors.InvalidTranslatorSessionIdError,
        "Translator Server"
    )


class AddsATrippleAAtTheBeginingTranslator(Translator.Translator):
    """This Translator exists only for testing purposes. It's used with two aims:
    1. To test that ProxyServer really calls the methods in Translator (it acts as a fake logger).
    2. To have a first example (executed when tests are runned) of a Translator that stores info in a session_manager.
    Since this Translators uses the SessionManager provided by ProxyServer, it can not be instanced as a stand-alone WebLab server."""

    @Override(Translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_on_start(self, session):
        session['log'] = "on_start "

    @Override(Translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_before_send_command(self, session, command):
        session['log'] += "before_send_command "
        return Command("AAA%s" % command.commandstring)

    @Override(Translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_after_send_command(self, session, response):
        session['log'] += "after_send_command "
        return Command("AAA%s" % response.commandstring)

    @Override(Translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_before_send_file(self, session, file):
        session['log'] += "before_send_file "
        file_content = ExperimentUtil.deserialize(file.commandstring)
        return Command(ExperimentUtil.serialize("AAA%s" % file_content))

    @Override(Translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_after_send_file(self, session, response):
        session['log'] += "after_send_file "
        return Command("AAA%s" % response.commandstring)

    @Override(Translator.Translator)
    @logged(log.level.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_on_finish(self, session):
        session['log'] += "do_on_finish "
        return Command(session['log'])
