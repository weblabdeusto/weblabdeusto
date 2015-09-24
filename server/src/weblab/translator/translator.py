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

class Translator(object):
    """Abstract"""
    """A Translator can be created in two different ways:
         1. Deployed as a stand-alone WebLab-Server, being created by Loader. In this case, the Translator will never
            receive a session_manager, because Loader can't send anything apart from the coord_address,
            the locator and the cfg_manager. Then, if the Translator wants to persist data among different
            methods, it'll have to manage that in its own (e.g: creating its own SessionManager [of the
            SessionType.sqlalchemy type, because a SessionType.Memory one will not work, obviously]).
         2. Instanced by the ProxyServer. This happens when the ProxyServer's Locator can't find any suitable
            Translator. Then, the ProxyServer creates the default one specified in the cfg_manager, being
            StoreEverythingTranslator the default value for that cfg property. In this case, the ProxyServer
            passes its own SessionManager to the Translator, so it can persist data easily."""

    def __init__(self, coord_address, locator, cfg_manager, session_manager=None, *args, **kargs):
        super(Translator, self).__init__(*args, **kargs)
        self._coord_address = coord_address
        self._easy_locator = locator
        self._cfg_manager = cfg_manager
        self._session_manager = session_manager #if session_manager is not None else self._create_session_manager()

    def get_coord_addr(self):
        return self._easy_locator.get_server_coordaddr()

    #
    # API
    #

    def do_on_start(self, session_id):
        pass

    def do_before_send_command(self, session_id, command):
        pass

    def do_after_send_command(self, session_id, response):
        pass

    def do_before_send_file(self, session_id, file):
        pass

    def do_after_send_file(self, session_id, response):
        pass

    def do_on_finish(self, session_id):
        pass

    #
    # Proxy methods to allow to use this class without using a ServerLocator
    #

    def on_start(self, *args, **kargs):
        return self.do_on_start(*args, **kargs)

    def before_send_command(self, *args, **kargs):
        return self.do_before_send_command(*args, **kargs)

    def after_send_command(self, *args, **kargs):
        return self.do_after_send_command(*args, **kargs)

    def before_send_file(self, *args, **kargs):
        return self.do_before_send_file(*args, **kargs)

    def after_send_file(self, *args, **kargs):
        return self.do_after_send_file(*args, **kargs)

    def on_finish(self, *args, **kargs):
        return self.do_on_finish(*args, **kargs)