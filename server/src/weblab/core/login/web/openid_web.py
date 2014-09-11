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

try:
    from urlparse import parse_qsl as url_parse_qsl
    parse_qsl = url_parse_qsl
except ImportError:
    from cgi import parse_qsl as cgi_parse_qsl
    parse_qsl = cgi_parse_qsl

try:
    from openid.store import memstore
    from openid.consumer import consumer
    from openid.oidutil import appendArgs
    from openid.cryptutil import randomString
except ImportError:
    OPENID_AVAILABLE = False
else:
    OPENID_AVAILABLE = True

import urlparse
import traceback
from Cookie import SimpleCookie

import voodoo.log as log
from voodoo.log import logged

import weblab.login.exc as LoginErrors
from weblab.core.login.web import WebPlugin, ExternalSystemManager

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
        return OpenIdPlugin.get_user_id(credentials)

class OpenIdPlugin(WebPlugin):

    path = '/openid/'

    SESSION_COOKIE_NAME = 'weblabopenid'
    host            = ''
    client_url      = ''
    base_openid_url = ''
    sessions = {}

    if OPENID_AVAILABLE:
        @classmethod
        def initialize(klass, cfg_manager, route):
            OpenIdPlugin.store    = memstore.MemoryStore()
            OpenIdPlugin.domains  = cfg_manager.get_value(DOMAINS_PROPERTY, DEFAULT_DOMAINS_PROPERTY)
            OpenIdPlugin.sessions = {}
            OpenIdPlugin.host     = cfg_manager.get_value(HOST_PROPERTY, DEFAULT_HOST)
            client_url = cfg_manager.get_value(CLIENT_URL_PROPERTY, None)
            if client_url is None:
                OpenIdPlugin.client_url = OpenIdPlugin.host + DEFAULT_CLIENT_URL
            else:
                OpenIdPlugin.client_url = client_url
            base_openid_url = cfg_manager.get_value(BASE_OPENID_URL, None)
            if base_openid_url is None:
                OpenIdPlugin.base_openid_url = OpenIdPlugin.host + DEFAULT_BASE_OPENID_URL
            else:
                OpenIdPlugin.base_openid_url = base_openid_url

        def __call__(self, environ, start_response):
            local = self.relative_path

            self.parsed_uri = urlparse.urlparse(self.uri)
            self.query = {}
            for k, v in parse_qsl(self.parsed_uri[4]):
                self.query[k] = v.decode('utf-8')

            if local.startswith('verify'):
                return self.verify()
            elif local.startswith('process'):
                return self.process()
            return_value = """<html><body><form method="GET" action="verify">
                    Username: <input type="text" name="username"><br>"""
            for university in self.domains:
                return_value += """<input type="radio" name="domain" value="%s">%s<br>""" % (university, university)
            return_value += """<input type="submit" value="Log in">
                </form></body></html>"""
            return self.build_response(return_value, content_type = 'text/html')

        def verify(self):
            domain = self.get_argument(DOMAIN)
            if domain is not None:
                if not domain.upper() in self.domains:
                    return self.build_response("domain provided but not supported by configuration. Check %s in settings" % DOMAINS_PROPERTY)
                username = self.get_argument(USERNAME)
                if username is None:
                    return self.build_response("When domain provided, a username must also be provided")
                domain_tpl = self.domains[domain.upper()]
                try:
                    full_url = domain_tpl % username
                except:
                    return self.build_response("Invalid domain. It must have a wildcard '%%s' within the URL. Instead '%s' found" % domain)
            else:
                full_url = self.get_argument(USER_ID)
                if full_url is None:
                    return self.build_response("A username (%s) + domain (%s) or a user identifier (%s) must be provided " % (USERNAME, DOMAIN, USER_ID))

            # full_url contains the user identifier
            try:
                request = self.consumer.begin(full_url)
            except consumer.DiscoveryFailure:
                traceback.print_exc()
                return self.build_response('Error in discovery, contact with administrator')
            else:
                if request is None:
                    return self.build_response("No OpenID services found. contact with administrator")
                else:
                    trust_root = self.host
                    return_to = self.build_url('process')
                    if request.shouldSendRedirect():
                        redirect_url = request.redirectURL( trust_root, return_to, immediate = False)
                        return self.build_response('Go to %s' % redirect_url, code = 302, headers = [ ('Location', redirect_url) ])
                    else:
                        form_html = request.formMarkup( trust_root, return_to, form_tag_attrs={'id':'openid_message'}, immediate=False)
                        return self.build_response(self.auto_submit(form_html, 'openid_message'), content_type = 'text/html')

        def process(self):
            url = self.host + self.uri
            info = self.consumer.complete(self.query, url)

            if info.status == consumer.SUCCESS:
                self.get_session()['validated'] = info.identity_url
                try:
                    session_id = self.server.extensible_login(OpenIdManager.NAME,'%s' % self.get_session()['id'])
                except LoginErrors.LoginError:
                    return self.build_response("Successfully authenticated; however your account does not seem to be registered in WebLab-Deusto. Do please contact with administrators")
                full_client_url = "%s?session_id=%s;%s" % (self.client_url, session_id.id, self.weblab_cookie)
                return self.build_response("<html><body><script>top.location.href='%s';</script><a href='%s'>Continue</a></body></html>" % (full_client_url, full_client_url), content_type = 'text/html')
            else:
                return self.build_response("failed to authenticate! %s; %s" % (info.status, info.message if hasattr(info, 'message') else ''))

        @classmethod
        def get_user_id(klass, credentials):
            session_id = credentials
            session = OpenIdPlugin.sessions.get(session_id)
            return session.get('validated', '')

        def build_url(self, action, **query):
            base = urlparse.urljoin(self.base_openid_url, action)
            return appendArgs(base, query)

        def auto_submit(self, form, id):
            return """<html><head><title>Transaction in progress</title></head>
                <body onload='document.getElementById("%s").submit()'>
                Requesting credentials...<br/>
                %s
                </body></html>
                """%(id, form)

        @property
        def consumer(self):
            return consumer.Consumer(self.get_session(), OpenIdPlugin.store)

        def get_session(self):
            if hasattr(self, 'session') and self.session is not None:
                return self.session

            # Get value of cookie header that was sent
            cookie_str = self.headers.get('Cookie')
            if cookie_str:
                cookie_obj = SimpleCookie(cookie_str)
                sid_morsel = cookie_obj.get(self.SESSION_COOKIE_NAME, None)
                if sid_morsel is not None:
                    sid = sid_morsel.value
                else:
                    sid = None
            else:
                sid = None

            # If a session id was not set, create a new one
            if sid is None:
                sid = randomString(16, '0123456789abcdef')
                session = None
            else:
                session = OpenIdPlugin.sessions.get(sid)

            # If no session exists for this session ID, create one
            if session is None:
                session = OpenIdPlugin.sessions[sid] = {}

            session['id'] = sid
            self.session = session
            return session
    else:
        @classmethod
        def get_user_id_withoutopenid(klass, credentials):
            return ""

        def run_withoutopenid(self, environ, start_response):
            return self.build_response("python-openid not found")

        __call__ = run_withoutopenid
        get_user_id = get_user_id_withoutopenid

