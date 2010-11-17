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
from weblab.data import ServerType
import weblab.translator.Translator as Translator


class StoresEverythingTranslator(Translator.Translator):
        
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    def do_on_start(self, session_id):
        super(StoresEverythingTranslator, self).do_on_start(session_id)
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_command(self, session_id, command):
        return command
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_command(self, session_id, response):
        return response
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    def do_before_send_file(self, session_id, file):
        return file
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    def do_after_send_file(self, session_id, response):
        return response
    
    @Override(Translator.Translator)
    @logged(LogLevel.Info)
    @caller_check(ServerType.Proxy)
    def do_on_finish(self, session_id):
        super(StoresEverythingTranslator, self).do_on_finish(session_id)