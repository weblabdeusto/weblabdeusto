#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import weblab.comm.WebFacadeServer as WebFacadeServer
import weblab.login.exc as LoginExceptions

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

class OpenIdMethod(WebFacadeServer.Method):
    path = '/openid/'
    SESSION_COOKIE_NAME = 'weblabopenid'
    host            = ''
    client_url      = ''
    base_openid_url = ''
    sessions = {}

    if OPENID_AVAILABLE:
        @classmethod
        def initialize(klass, cfg_manager, route):
            OpenIdMethod.store    = memstore.MemoryStore()
            OpenIdMethod.domains  = cfg_manager.get_value(DOMAINS_PROPERTY, DEFAULT_DOMAINS_PROPERTY)
            OpenIdMethod.sessions = {}
            OpenIdMethod.host     = cfg_manager.get_value(HOST_PROPERTY, DEFAULT_HOST)
            client_url = cfg_manager.get_value(CLIENT_URL_PROPERTY, None)
            if client_url is None:
                OpenIdMethod.client_url = OpenIdMethod.host + DEFAULT_CLIENT_URL
            else:
                OpenIdMethod.client_url = client_url
            base_openid_url = cfg_manager.get_value(BASE_OPENID_URL, None)
            if base_openid_url is None:
                OpenIdMethod.base_openid_url = OpenIdMethod.host + DEFAULT_BASE_OPENID_URL
            else:
                OpenIdMethod.base_openid_url = base_openid_url

        def get_local_relative_path(self):
            return self.relative_path[len(self.path):]

        def run(self):
            local = self.get_local_relative_path()

            self.parsed_uri = urlparse.urlparse(self.req.path)
            self.query = {}
            for k, v in parse_qsl(self.parsed_uri[4]):
                self.query[k] = v.decode('utf-8')

            if local.startswith('verify'):
                return self.doVerify()
            elif local.startswith('process'):
                return self.doProcess()
            return_value = """<html><body><form method="GET" action="verify">
                    Username: <input type="text" name="username"><br>"""
            for university in self.domains:
                return_value += """<input type="radio" name="domain" value="%s">%s<br>""" % (university, university)
            return_value += """<input type="submit" value="Log in">
                </form></body></html>"""
            return return_value

        def doVerify(self):
            domain = self.get_argument(DOMAIN)
            if domain is not None:
                if not domain.upper() in self.domains:
                    return "domain provided but not supported by configuration. Check %s in settings" % DOMAINS_PROPERTY
                username = self.get_argument(USERNAME)
                if username is None:
                    return "When domain provided, a username must also be provided"
                domain_tpl = self.domains[domain.upper()]
                try:
                    full_url = domain_tpl % username
                except:
                    return "Invalid domain. It must have a wildcard '%%s' within the URL. Instead '%s' found" % domain
            else:
                full_url = self.get_argument(USER_ID)
                if full_url is None:
                    return "A username (%s) + domain (%s) or a user identifier (%s) must be provided " % (USERNAME, DOMAIN, USER_ID)
            
            # full_url contains the user identifier
            oidconsumer = self.getConsumer()
            try:
                request = oidconsumer.begin(full_url)
            except consumer.DiscoveryFailure:
                traceback.print_exc()
                return 'Error in discovery, contact with administrator'
            else:
                if request is None:
                    return "No OpenID services found. contact with administrator"
                else:
                    trust_root = self.host
                    return_to = self.buildURL('process')
                    if request.shouldSendRedirect():
                        redirect_url = request.redirectURL( trust_root, return_to, immediate = False)
                        self.req.send_response(302)
                        self.req.send_header('Location', redirect_url)
                        self.req.end_headers()
                        raise WebFacadeServer.RequestManagedException()
                    else:
                        form_html = request.formMarkup( trust_root, return_to, form_tag_attrs={'id':'openid_message'}, immediate=False)
                        return self.autoSubmit(form_html, 'openid_message')

        def doProcess(self):
            oidconsumer = self.getConsumer()

            url = self.host + self.req.path
            info = oidconsumer.complete(self.query, url)

            if info.status == consumer.SUCCESS:
                self.getSession()['validated'] = info.identity_url
                try:
                    session_id = self.server.extensible_login('OPENID','%s' % self.getSession()['id'])
                except LoginExceptions.LoginException:
                    return "Successfully authenticated; however your account does not seem to be registered in WebLab-Deusto. Do please contact with administrators"
                full_client_url = "%s?session_id=%s;%s" % (self.client_url, session_id.id, self.weblab_cookie)
                return "<html><body><script>top.location.href='%s';</script><a href='%s'>Continue</a></body></html>" % (full_client_url, full_client_url)
            else:
                return "failed to authenticate!"

        @classmethod
        def get_user_id(klass, credentials):
            session_id = credentials
            session = OpenIdMethod.sessions.get(session_id)
            return session.get('validated', '')

        def buildURL(self, action, **query):
            base = urlparse.urljoin(self.base_openid_url, action)
            return appendArgs(base, query)

        def autoSubmit(self, form, id):
            return """<html><head><title>Transaction in progress</title></head>
                <body onload='document.getElementById("%s").submit()'>
                Requesting credentials...<br/>
                %s
                </body></html>
                """%(id, form)

        def getConsumer(self):
            return consumer.Consumer(self.getSession(), OpenIdMethod.store)

        def getSession(self):
            if hasattr(self, 'session') and self.session is not None:
                return self.session

            # Get value of cookie header that was sent
            cookie_str = self.req.headers.get('Cookie')
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
                session = OpenIdMethod.sessions.get(sid)

            # If no session exists for this session ID, create one
            if session is None:
                session = OpenIdMethod.sessions[sid] = {}

            session['id'] = sid
            self.session = session
            return session
    else:
        @classmethod
        def get_user_id_withoutopenid(klass, credentials):
            return ""

        def run_withoutopenid(self):
            return "python-openid not found"

        run = run_withoutopenid
        get_user_id = get_user_id_withoutopenid

