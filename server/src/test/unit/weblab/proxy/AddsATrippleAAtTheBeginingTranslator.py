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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

from voodoo import LogLevel
from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
from voodoo.override import Override
from voodoo.sessions.SessionChecker import check_session
from weblab.data import ServerType
from weblab.exceptions.translator import TranslatorExceptions
import weblab.translator.Translator as Translator
import weblab.experiment.Util as ExperimentUtil


check_session_params = (
        TranslatorExceptions.InvalidTranslatorSessionIdException,
        "Translator Server"
    )


class AddsATrippleAAtTheBeginingTranslator(Translator.Translator):
    """This Translator exists only for testing purposes. It's used with two aims:
    1. To test that ProxyServer really calls the methods in Translator (it acts as a fake logger).
    2. To have a first example (executed when tests are runned) of a Translator that stores info in a session_manager.
    Since this Translators uses the SessionManager provided by ProxyServer, it can not be instanced as a stand-alone WebLab server."""  
            
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_on_start(self, session):
        session['log'] = "on_start "
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_before_send_command(self, session, command):
        session['log'] += "before_send_command "
        return "AAA%s" % command
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_after_send_command(self, session, response):
        session['log'] += "after_send_command "
        return "AAA%s" % response
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_before_send_file(self, session, file):
        session['log'] += "before_send_file "
        file_content = ExperimentUtil.deserialize(file)
        return ExperimentUtil.serialize("AAA%s" % file_content)
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_after_send_file(self, session, response):
        session['log'] += "after_send_file "
        return "AAA%s" % response
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    @check_session(*check_session_params)
    def do_on_finish(self, session):
        session['log'] += "do_on_finish "
        return session['log']