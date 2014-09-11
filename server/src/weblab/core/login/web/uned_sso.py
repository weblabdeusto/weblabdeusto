#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#

import urllib
import base64

import voodoo.log as log
from voodoo.log import logged


from weblab.core.login.web import WebPlugin, ExternalSystemManager
import weblab.login.exc as LoginErrors

from weblab.data.dto.users import User
from weblab.data.dto.users import StudentRole

try:
    from M2Crypto import BIO, RSA, EVP
except ImportError:
    M2CRYPTO_AVAILABLE = False
else:
    M2CRYPTO_AVAILABLE = True

PEM_FILE_PATH = ''

def process_cookie(original_message):
    unquoted_message = urllib.unquote(original_message)
    payload   = unquoted_message[:unquoted_message.rfind('#')]
    base64_signature = unquoted_message[unquoted_message.rfind('#')+1:]

    signature = base64.decodestring(base64_signature)
    
    try:
        pem = open(PEM_FILE_PATH).read()
    except:
        raise Exception("Could not open PEM file")

    bio = BIO.MemoryBuffer(pem)
    rsa = RSA.load_pub_key_bio(bio)
    pubkey = EVP.PKey()
    pubkey.assign_rsa(rsa)
    pubkey.reset_context(md='sha1')
    pubkey.verify_init()
    pubkey.verify_update(payload)
    return_value = pubkey.verify_final(signature)
    if not return_value:
        raise Exception("UNED cookie not verified")

    user_id = ''
    email   = ''

    for elem in payload.split('#'):
        if elem.startswith('ID:'):
            user_id = base64.decodestring(elem.split(':')[1])
        elif elem.startswith('EMAIL:'):
            email = base64.decodestring(elem.split(':')[1])

    return user_id, email

class UnedSSOManager(ExternalSystemManager):

    NAME = 'UNED-SSO'
    PEM_FILE_PATH = ''

    @logged(log.level.Warning)
    def get_user(self, credentials):

        if not M2CRYPTO_AVAILABLE:
            raise Exception("M2Crypto module not available")
       
        user_id, email = process_cookie(credentials) 

        login = '%s@uned' % email
        full_name = user_id # We don't know the full name
        return User(login, full_name, email, StudentRole())

    def get_user_id(self, credentials):

        if not M2CRYPTO_AVAILABLE:
            raise Exception("M2Crypto module not available")

        return self.get_user(credentials).email


class UnedSSOPlugin(WebPlugin):
    path = '/unedsso/'

    def __init__(self, *args, **kwargs):
        super(UnedSSOPlugin, self).__init__(*args, **kwargs)

        global PEM_FILE_PATH
        PEM_FILE_PATH = self.cfg_manager.get_value('uned_sso_public_key_path', '')

    def __call__(self, environ, start_response):
        uned_sso = self.cfg_manager.get_value('uned_sso', False)

        if not uned_sso:
            return self.build_response("<html><body>UNED SSO system disabled</body></html>")

        if not M2CRYPTO_AVAILABLE:
            return self.build_response("<html><body>M2Crypto module not available</body></html>", content_type = 'text/html')

        cookies = environ.get('HTTP_COOKIE', '').split('; ')
        payload = ''
        for cookie in cookies:
            if cookie.startswith('usuarioUNEDv2='):
                payload = '='.join(cookie.split('=')[1:])

        if payload:
            try:
                session_id = self.server.extensible_login(UnedSSOManager.NAME, payload)
            except LoginErrors.InvalidCredentialsError:
                try:
                    _, email = process_cookie(payload)
                except:
                    return self.build_response("Invalid cookie found!")
                else:
                    return self.build_response("%s: you were verified, but you are not registered in this WebLab-Deusto instance. Contact the administrator." % email)
            else:
                return self._show_weblab(session_id)
        else:
            url = self.cfg_manager.get_value('core_server_url', 'core_server_url NOT SET')
            current_url = url + 'login/web/unedsso/'
            return self.build_response("Redirecting to sso.uned.es...", code = 302, headers = [('Location', 'https://sso.uned.es/sso/index.aspx?URL=' + current_url)])

    def _show_weblab(self, session_id):
        base_url = self.cfg_manager.get_value('core_server_url', 'core_server_url NOT SET')
        base_client_url = base_url + "client/"
        url = '%s#session_id=%s;%s.%s' % (base_client_url, session_id.id, session_id.id, self.server_route)
        return self.build_response("Redirecting to WebLab-Deusto...", code = 302, headers = [('Location', url)])


