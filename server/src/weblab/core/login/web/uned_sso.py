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
from __future__ import print_function, unicode_literals

import urllib
import base64

import voodoo.log as log
from voodoo.log import logged

from flask import request, make_response, redirect
from weblab.core.login.web import weblab_api

from weblab.core.login.web import ExternalSystemManager
import weblab.core.login.exc as LoginErrors

from weblab.data.dto.users import User
from weblab.data.dto.users import StudentRole

try:
    from M2Crypto import BIO, RSA, EVP
except ImportError:
    M2CRYPTO_AVAILABLE = False
else:
    M2CRYPTO_AVAILABLE = True

PEM_FILE_PATH = None
UNED_SSO = None

def process_cookie(original_message):
    unquoted_message = urllib.unquote(original_message)
    payload   = unquoted_message[:unquoted_message.rfind('#')]
    base64_signature = unquoted_message[unquoted_message.rfind('#')+1:]

    signature = base64.decodestring(base64_signature)
    
    try:
        pem = open(PEM_FILE_PATH or '').read()
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

@weblab_api.route_login_web('/unedsso/')
def uned_sso():
    # Initialize global variables if not previously done
    global PEM_FILE_PATH, UNED_SSO
    if PEM_FILE_PATH is None:
        PEM_FILE_PATH = weblab_api.config.get_value('uned_sso_public_key_path', '')
        UNED_SSO = weblab_api.config.get_value('uned_sso', False)

    # Reject user if UNED_SSO is not available
    if not UNED_SSO:
        return make_response("<html><body>UNED SSO system disabled</body></html>", content_type = 'text/html')

    if not M2CRYPTO_AVAILABLE:
        return make_response("<html><body>M2Crypto module not available</body></html>", content_type = 'text/html')

    payload = request.cookies.get('usuarioUNEDv2', '')

    if payload:
        try:
            session_id = weblab_api.api.extensible_login(UnedSSOManager.NAME, payload)
        except LoginErrors.InvalidCredentialsError:
            try:
                _, email = process_cookie(payload)
            except:
                return "Invalid cookie found!"
            else:
                return "%s: you were verified, but you are not registered in this WebLab-Deusto instance. Contact the administrator." % email
        else:
            base_client_url = weblab_api.ctx.core_server_url + "client/"
            url = '%s#session_id=%s;%s.%s' % (base_client_url, session_id.id, session_id.id, weblab_api.ctx.route)
            return redirect(url)
    else:
        return redirect('https://sso.uned.es/sso/index.aspx?URL=' + request.url)

