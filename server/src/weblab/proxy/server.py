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
from voodoo.sessions import session_type as SessionType, manager as SessionManager, session_id as SessionId
from voodoo.sessions.checker import check_session
from weblab.data import server_type as ServerType
import weblab.proxy.exc as ProxyErrors
from weblab.proxy import session_handler as ProxySessionHandler
from weblab.translator.translators import StoresEverythingTranslator, StoresNothingTranslator, StoresEverythingExceptForFilesTranslator


WEBLAB_PROXY_SERVER_SESSION_TYPE                    = "proxy_session_type"
WEBLAB_PROXY_SERVER_SESSION_POOL_ID                 = "proxy_session_pool_id"
WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME         = "proxy_session_default_translator_name"

DEFAULT_WEBLAB_PROXY_SERVER_SESSION_TYPE            = SessionType.Memory
DEFAULT_WEBLAB_PROXY_SERVER_SESSION_POOL_ID         = "ProxyServer"
DEFAULT_WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME = "StoresEverythingTranslator"

check_session_params = (
        ProxyErrors.InvalidReservationIdError,
        "Proxy Server"
    )


DEFAULT_TRANSLATORS = { 'StoresEverythingTranslator': StoresEverythingTranslator,
                        'StoresEverythingExceptForFilesTranslator': StoresEverythingExceptForFilesTranslator,
                        'StoresNothingTranslator': StoresNothingTranslator }


def access_enabled_required(func):
    """
    Decorator to be used by every ProxyServer method that requires the access being enabled.
    """
    def wrapped(self, session, *args, **kargs):
        if not session['access_enabled']:
            raise ProxyErrors.AccessDisabledError("Access is disabled for the provided reservation_id in this Proxy: %s" % session['reservation_id'])
        return func(self, session, *args, **kargs)
    wrapped.__name__ = func.__name__
    wrapped.__doc__ = func.__doc__
    return wrapped


class ProxyServer(object):
    """
    The lifecycle is as follows:
        1. Core enables access so Proxy creates a dict with the session data.
        2. Facade can access the experiment.
        3. Core disables access so Proxy marks the 'access_enabled' field as False.
        4. Core asks for the results and Proxy removes the dict.
    """

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(ProxyServer,self).__init__(*args, **kwargs)
        self._coord_address = coord_address
        self._locator = locator
        self._cfg_manager = cfg_manager
        self._session_manager = self._create_session_manager()
        self._default_translator_klazz = self._read_default_translator_klazz()

    def _create_default_translator(self):
        return self._default_translator_klazz(self._coord_address, self._locator, self._cfg_manager, self._session_manager)

    def _load_translator(self, session):
        if session['trans_coord_addr'] is not None:
            return self._locator[session['trans_coord_addr']]
        else:
            return self._create_default_translator()

    def _load_laboratory(self, session):
        return self._locator[session['lab_coord_addr']]

    def _load_proxy_session_handler(self, session):
        translator = self._load_translator(session)
        laboratory = self._load_laboratory(session)
        return ProxySessionHandler.ProxySessionHandler(
                    session,
                    laboratory,
                    translator,
                    self._cfg_manager, self._locator, self._session_manager
        )

    def _create_session_manager(self):
        session_type = self._cfg_manager.get_value(WEBLAB_PROXY_SERVER_SESSION_TYPE, DEFAULT_WEBLAB_PROXY_SERVER_SESSION_TYPE)
        session_pool_id   = self._cfg_manager.get_value(WEBLAB_PROXY_SERVER_SESSION_POOL_ID, DEFAULT_WEBLAB_PROXY_SERVER_SESSION_POOL_ID)
        if session_type in SessionType.getSessionTypeValues():
            return SessionManager.SessionManager(self._cfg_manager, session_type, session_pool_id)
        else:
            raise ProxyErrors.NotASessionTypeError('Not a session type: %s' % session_type)

    def _read_default_translator_klazz(self):
        klazz_name = self._cfg_manager.get_value(WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME, DEFAULT_WEBLAB_PROXY_SERVER_DEFAULT_TRANSLATOR_NAME)
        if klazz_name not in DEFAULT_TRANSLATORS:
            raise ProxyErrors.InvalidDefaultTranslatorNameError("Provided: %s. Valids: %s" % (klazz_name, DEFAULT_TRANSLATORS.keys()))
        return DEFAULT_TRANSLATORS[klazz_name]

    def _find_translator(self, experiment_unique_id):
        potential_translators = self._locator.find_by_type(ServerType.Translator)
        if potential_translators:
            is_default = False
            translator = self._locator[potential_translators[0]]
        else:
            translator = self._create_default_translator()
            is_default = True

        return translator, is_default

    #===========================================================================
    # API to Core Server
    #===========================================================================

    @caller_check(ServerType.UserProcessing)
    @logged(log.level.Info)
    def do_enable_access(self, reservation_id, experiment_unique_id, user_login, lab_coord_addr, lab_sess_id):
        translator, is_a_default_translator = self._find_translator(experiment_unique_id)
        # The Translator's session_id must be different because every session_id is protected with a threading.Lock
        trans_session_id = self._session_manager.create_session("tr:%s" % reservation_id)
        proxy_sess_id = self._session_manager.create_session(reservation_id)
        data = {
                'reservation_id': reservation_id,
                'user_login': user_login,
                'lab_coord_addr': lab_coord_addr,
                'lab_sess_id': lab_sess_id,
                'trans_session_id': trans_session_id,
                'trans_coord_addr': translator.get_coord_addr() if not is_a_default_translator else None,
                'commands': [],
                'files': []
               }
        self._session_manager.modify_session(proxy_sess_id, data)
        proxy_session_handler = self._load_proxy_session_handler(data)
        try:
            return proxy_session_handler.enable_access()
        finally:
            proxy_session_handler.update_latest_timestamp()

    @caller_check(ServerType.UserProcessing)
    @logged(log.level.Info)
    def do_are_expired(self, session_ids):
        expirations = []
        for session_id in session_ids:
            sess_id = SessionId.SessionId(session_id)
            if self._session_manager.has_session(sess_id):
                session = self._session_manager.get_session_locking(sess_id)
                proxy_session_handler = self._load_proxy_session_handler(session)
                try:
                    is_expired = proxy_session_handler.is_expired()
                finally:
                    proxy_session_handler.update_latest_timestamp()
            else:
                is_expired = "Y <sessionid-not-found>"
            expirations.append(is_expired)
        return expirations

    @caller_check(ServerType.UserProcessing)
    @logged(log.level.Info)
    @check_session(*check_session_params)
    @access_enabled_required
    def do_disable_access(self, session):
        proxy_session_handler = self._load_proxy_session_handler(session)
        try:
            return proxy_session_handler.disable_access()
        finally:
            proxy_session_handler.update_latest_timestamp()

    @caller_check(ServerType.UserProcessing)
    @logged(log.level.Info)
    def do_retrieve_results(self, session_id):
        sess_id = SessionId.SessionId(session_id)
        session = self._session_manager.get_session_locking(sess_id)
        try:
            proxy_session_handler = self._load_proxy_session_handler(session)
            try:
                return proxy_session_handler.retrieve_results()
            finally:
                proxy_session_handler.update_latest_timestamp()
        finally:
            self._session_manager.delete_session_unlocking(sess_id)

    #===========================================================================
    # API to Client
    #===========================================================================

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @access_enabled_required
    def poll(self, session):
        proxy_session_handler = self._load_proxy_session_handler(session)
        try:
            return proxy_session_handler.poll()
        finally:
            proxy_session_handler.update_latest_timestamp()

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @access_enabled_required
    def send_command(self, session, command):
        proxy_session_handler = self._load_proxy_session_handler(session)
        try:
            return proxy_session_handler.send_command(command)
        finally:
            proxy_session_handler.update_latest_timestamp()

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @access_enabled_required
    def send_file(self, session, file_content, file_info):
        proxy_session_handler = self._load_proxy_session_handler(session)
        try:
            return proxy_session_handler.send_file(file_content, file_info)
        finally:
            proxy_session_handler.update_latest_timestamp()
