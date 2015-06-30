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

import json
import urllib2
import base64
from flask import make_response, render_template, request

import voodoo.log as log
from voodoo.log import logged

from weblab.core.login.web import weblab_api, get_argument 
from weblab.core.login.web import ExternalSystemManager
import weblab.core.login.exc as LoginErrors

from weblab.data.dto.users import User
from weblab.data.dto.users import StudentRole


REQUEST_FIELD           = 'signed_request'
FACEBOOK_APP_PROPERTY   = "login_facebook_url"
CLIENT_ADDRESS_PROPERTY = "login_facebook_client_address"
AUTH_URL_PROPERTY       = "login_facebook_auth_url"
DEFAULT_AUTH_URL        = "http://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=email"
APP_ID_PROPERTY         = "login_facebook_app_id"
CANVAS_URL_PROPERTY     = "login_facebook_canvas_url"

FACEBOOK_TOKEN_VALIDATOR = "https://graph.facebook.com/me?access_token=%s"

# TODO: this could be refactored to be more extensible for other OAuth systems
class FacebookManager(ExternalSystemManager):

    NAME = 'FACEBOOK'

    @logged(log.level.Warning)
    def get_user(self, credentials):
        payload = credentials[credentials.find('.') + 1:]
        payload = payload.replace('-','+').replace('_','/')
        payload = payload + "=="
        try:
            json_content = base64.decodestring(payload)
            data = json.loads(json_content)
            oauth_token = data['oauth_token']
            req = urllib2.urlopen(FACEBOOK_TOKEN_VALIDATOR % oauth_token)
            encoding = req.headers['content-type'].split('charset=')[-1]
            ucontent = unicode(req.read(),encoding)
            user_data = json.loads(ucontent)
            if not user_data['verified']:
                raise Exception("Not verified user!!!")
            login = '%s@facebook' % user_data['id']
            full_name = user_data['name']
            email = user_data.get('email','<not provided>')
            user = User(login, full_name, email, StudentRole())
            return user
        except Exception as e:
            log.log( FacebookManager, log.level.Warning, "Error: %s" % e )
            log.log_exc( FacebookManager, log.level.Info )
            return ""

    def get_user_id(self, credentials):
        login = self.get_user(credentials).login
        # login is "13122142321@facebook"
        return login.split('@')[0]

@weblab_api.route_login_web('/facebook/', methods = ['GET', 'POST'])
def facebook():
    signed_request = get_argument(REQUEST_FIELD)

    if signed_request is None:
        facebook_app = weblab_api.config.get_value(FACEBOOK_APP_PROPERTY, None)
        if facebook_app is None:
            return "<html><body>%s not set. Contact administrator</body></html>" % FACEBOOK_APP_PROPERTY
        return "<html><body><script>top.location.href='%s';</script></body></html>" % facebook_app

    payload = signed_request[signed_request.find('.') + 1:]
    payload = payload.replace('-','+').replace('_','/')
    payload = payload + "=="
    json_content = base64.decodestring(payload)
    data = json.loads(json_content)
    if 'user_id' not in data:
        base_auth_url = weblab_api.config.get_value(AUTH_URL_PROPERTY, DEFAULT_AUTH_URL)
        facebook_app_id = weblab_api.config.get_value(APP_ID_PROPERTY)
        canvas_url = weblab_api.config.get_value(CANVAS_URL_PROPERTY)

        auth_url = base_auth_url % (facebook_app_id, urllib2.quote(canvas_url))

        return "<html><body><script>top.location.href='%s';</script></body></html>" % auth_url

    try:
        session_id = weblab_api.api.extensible_login(FacebookManager.NAME, signed_request)
    except LoginErrors.InvalidCredentialsError:
        return _handle_unauthenticated_clients(signed_request)

    return _show_weblab(session_id, signed_request)

def _show_weblab(session_id, signed_request):
    payload = signed_request[signed_request.find('.') + 1:]
    payload = payload.replace('-','+').replace('_','/')
    payload = payload + "=="
    json_content = base64.decodestring(payload)
    data = json.loads(json_content)
    locale = ''
    if 'user' in data:
        if 'locale' in data['user']:
            locale = "&locale=%s" % data['user']['locale']

    client_address = weblab_api.config.get_value(CLIENT_ADDRESS_PROPERTY, "%s NOT SET" % CLIENT_ADDRESS_PROPERTY)
    facebook_app_id = weblab_api.config.get_value(APP_ID_PROPERTY)

    return render_template('login_web/facebook_weblab.html', 
                client_address = client_address, session_id = '%s;%s' % (session_id.id, weblab_api.ctx.route), 
                locale = locale, facebook_app_id = facebook_app_id)

def _handle_unauthenticated_clients(signed_request):
    if get_argument('op','').lower() in ('create', 'link'):
        try:
            if get_argument('op','').lower() == 'create':
                session_id = weblab_api.api.create_external_user(FacebookManager.NAME, signed_request)
            else: # get_argument('op','').lower() == 'link'
                username = get_argument('username')
                password = get_argument('password')
                session_id = weblab_api.api.grant_external_credentials(username, password, FacebookManager.NAME, signed_request)
        except LoginErrors.InvalidCredentialsError:
            return make_response("Invalid username or password!", 403)
        else:
            return _show_weblab(session_id, signed_request)

    link_uri = request.url + '?op=link'
    create_uri = request.url + '?op=create'

    return render_template('login_web/facebook_unauthenticated.html', 
                    link_uri = link_uri, create_uri = create_uri,
                    signed_request = signed_request)
