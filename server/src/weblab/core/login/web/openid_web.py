#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

try:
    from openid.store import memstore
    from openid.consumer import consumer
    from openid.cryptutil import randomString
except ImportError:
    OPENID_AVAILABLE = False
else:
    OPENID_AVAILABLE = True

import traceback

from flask import request, url_for, redirect, make_response

import voodoo.log as log
from voodoo.log import logged

from weblab.core.login.web import weblab_api, get_argument 
import weblab.core.login.exc as LoginErrors
from weblab.core.login.web import ExternalSystemManager

USERNAME = "username"
DOMAIN   = "domain"
USER_ID  = "user_id"
DOMAINS_PROPERTY = "login_openid_domains"
DEFAULT_DOMAINS_PROPERTY = {
    'UNED'        : 'http://yo.rediris.es/soy/%s@uned.es',
    'UNED-INNOVA' : 'http://yo.rediris.es/soy/%s@innova.uned.es',
    'DEUSTO'      : 'http://yo.rediris.es/soy/%s@deusto.es'
}
HOST_PROPERTY            = 'login_openid_host'
DEFAULT_HOST             = 'https://www.weblab.deusto.es'
CLIENT_URL_PROPERTY      = 'login_openid_client_url'
DEFAULT_CLIENT_URL       = '/weblab/client/'
BASE_OPENID_URL          = 'login_openid_base_openid'
DEFAULT_BASE_OPENID_URL  = '/weblab/login/web/openid/'

class OpenIdManager(ExternalSystemManager):

    NAME = 'OPENID'

    @logged(log.level.Warning)
    def get_user(self, credentials):
        return None

    def get_user_id(self, credentials):
        session_id = credentials
        session = SESSIONS.get(session_id)
        return session.get('validated', '')

# TODO: These are global variables. If they go to different processors
# they will be broken. It should rely on Redis, SQL or so.
# https://github.com/weblabdeusto/weblabdeusto/issues/86
SESSION_COOKIE_NAME = 'weblabopenid'

INITIALIZED = False
HOST = ''
CLIENT_URL = ''
BASE_OPENID_URL = ''
SESSIONS = {}
STORE = None
DOMAINS = {}

def initialize():
    global INITIALIZED, HOST, CLIENT_URL, BASE_OPENID_URL, SESSIONS, DOMAINS, STORE
    if not INITIALIZED:
        INITIALIZED = True
        STORE = memstore.MemoryStore()
        DOMAINS = weblab_api.config.get_value(DOMAINS_PROPERTY, DEFAULT_DOMAINS_PROPERTY) or {}
        SESSIONS = {}
        HOST     = weblab_api.config.get_value(HOST_PROPERTY, DEFAULT_HOST)
        client_url = weblab_api.config.get_value(CLIENT_URL_PROPERTY, None)
        if client_url is None:
            CLIENT_URL = HOST + DEFAULT_CLIENT_URL
        else:
            CLIENT_URL = client_url
        base_openid_url = weblab_api.config.get_value(BASE_OPENID_URL, None)
        if base_openid_url is None:
            BASE_OPENID_URL  = HOST + DEFAULT_BASE_OPENID_URL
        else:
            BASE_OPENID_URL= base_openid_url

@weblab_api.route_login_web('/openid/', methods = ['GET', 'POST'])
def openid():
    if not OPENID_AVAILABLE:
        return "python-openid not found / not installed. Contact administrator."

    initialize()

    return_value = """<html><body><form method="GET" action="verify">
            Username: <input type="text" name="username"><br>"""
    for university in DOMAINS:
        return_value += """<input type="radio" name="domain" value="%s">%s<br>""" % (university, university)
    return_value += """<input type="submit" value="Log in">
        </form></body></html>"""
    return return_value

def get_session():
    # Get value of cookie header that was sent
    sid = request.cookies.get(SESSION_COOKIE_NAME)

    # If a session id was not set, create a new one
    if sid is None:
        sid = randomString(16, '0123456789abcdef')
        session = None
    else:
        session = SESSIONS.get(sid)

    # If no session exists for this session ID, create one
    if session is None:
        session = SESSIONS[sid] = {}

    session['id'] = sid
    return session

def get_consumer():
    return consumer.Consumer(get_session(), STORE)

@weblab_api.route_login_web('/openid/verify', methods = ['GET', 'POST'])
def openid_verify():
    if not OPENID_AVAILABLE:
        return "python-openid not found / not installed. Contact administrator."

    initialize()

    domain = get_argument(DOMAIN)
    if domain is not None:
        if not domain.upper() in DOMAINS:
            return make_response("domain provided but not supported by configuration. Check %s in settings" % DOMAINS_PROPERTY, 400)
        username = get_argument(USERNAME)
        if username is None:
            return make_response("When domain provided, a username must also be provided", 400)
        domain_tpl = DOMAINS[domain.upper()]
        try:
            full_url = domain_tpl % username
        except:
            return make_response("Invalid domain. It must have a wildcard '%%s' within the URL. Instead '%s' found" % domain, 400)
    else:
        full_url = get_argument(USER_ID)
        if full_url is None:
            return make_response("A username (%s) + domain (%s) or a user identifier (%s) must be provided " % (USERNAME, DOMAIN, USER_ID), 400)

    # full_url contains the user identifier
    current_consumer = get_consumer()
    try:
        current_request = current_consumer.begin(full_url)
    except consumer.DiscoveryFailure:
        traceback.print_exc()
        return make_response('Error in discovery, contact with administrator', 500)
    else:
        if current_request is None:
            return make_response("No OpenID services found. contact with administrator", 500)
        else:
            trust_root = request.host
            return_to = url_for('.openid_process', _external = True)
            if current_request.shouldSendRedirect():
                redirect_url = current_request.redirectURL( trust_root, return_to, immediate = False)
                return redirect(redirect_url) 
            else:
                form_html = current_request.formMarkup( trust_root, return_to, form_tag_attrs={'id':'openid_message'}, immediate=False)
                return """<html><head><title>Transaction in progress</title></head>
                        <body onload='document.getElementById("%s").submit()'>
                        Requesting credentials...<br/>
                        %s
                        </body></html>
                        """ % ('openid_message', form_html)

@weblab_api.route_login_web('/openid/process', methods = ['GET', 'POST'])
def openid_process():
    if not OPENID_AVAILABLE:
        return "python-openid not found / not installed. Contact administrator."

    initialize()

    current_consumer = get_consumer()
    info = current_consumer.complete(request.args, request.url)
    session = get_session()

    if info.status == consumer.SUCCESS:
        session['validated'] = info.identity_url
        try:
            session_id = weblab_api.api.extensible_login(OpenIdManager.NAME,'%s' % session['id'])
        except LoginErrors.LoginError:
            return "Successfully authenticated; however your account does not seem to be registered in WebLab-Deusto. Do please contact with administrators"
        client_url = weblab_api.ctx.core_server_url + 'client/'
        full_client_url = "%s?session_id=%s;%s.%s" % (client_url, session_id.id, session_id.id, weblab_api.ctx.route)
        return redirect(full_client_url)
    else:
        return make_response("failed to authenticate! %s; %s" % (info.status, info.message if hasattr(info, 'message') else ''), 403)

