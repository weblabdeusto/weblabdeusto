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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import urllib2
import base64

import weblab.comm.web_server as WebFacadeServer
import weblab.login.exc as LoginExceptions

REQUEST_FIELD           = 'signed_request'
FACEBOOK_APP_PROPERTY   = "login_facebook_url"
CLIENT_ADDRESS_PROPERTY = "login_facebook_client_address"
AUTH_URL_PROPERTY       = "login_facebook_auth_url"
DEFAULT_AUTH_URL        = "http://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=email"
APP_ID_PROPERTY         = "login_facebook_app_id"
CANVAS_URL_PROPERTY     = "login_facebook_canvas_url"

import json

class FacebookMethod(WebFacadeServer.Method):
    path = '/facebook/'

    def get_local_relative_path(self):
        return self.relative_path[len(self.path)+1:]

    def run(self):
        signed_request = self.get_argument(REQUEST_FIELD)
        if signed_request is None:
            facebook_app = self.cfg_manager.get_value(FACEBOOK_APP_PROPERTY, None)
            if facebook_app is None:
                return "<html><body>%s not set. Contact administrator</body></html>" % FACEBOOK_APP_PROPERTY
            return "<html><body><script>top.location.href='%s';</script></body></html>" % facebook_app

        payload = signed_request[signed_request.find('.') + 1:]
        payload = payload.replace('-','+').replace('_','/')
        payload = payload + "=="
        json_content = base64.decodestring(payload)
        data = json.loads(json_content)
        if 'user_id' not in data:
            base_auth_url = self.cfg_manager.get_value(AUTH_URL_PROPERTY, DEFAULT_AUTH_URL)
            facebook_app_id = self.cfg_manager.get_value(APP_ID_PROPERTY)
            canvas_url = self.cfg_manager.get_value(CANVAS_URL_PROPERTY)

            auth_url = base_auth_url % (facebook_app_id, urllib2.quote(canvas_url))

            return "<html><body><script>top.location.href='%s';</script></body></html>" % auth_url

        try:
            session_id = self.server.extensible_login('FACEBOOK', signed_request)
        except LoginExceptions.InvalidCredentialsException:
            return self._handle_unauthenticated_clients(signed_request)

        return self._show_weblab(session_id, signed_request)

    def _show_weblab(self, session_id, signed_request):
        payload = signed_request[signed_request.find('.') + 1:]
        payload = payload.replace('-','+').replace('_','/')
        payload = payload + "=="
        json_content = base64.decodestring(payload)
        data = json.loads(json_content)
        locale = ''
        if 'user' in data:
            if 'locale' in data['user']:
                locale = "&locale=%s" % data['user']['locale']

        client_address = self.cfg_manager.get_value(CLIENT_ADDRESS_PROPERTY, "%s NOT SET" % CLIENT_ADDRESS_PROPERTY)
        facebook_app_id = self.cfg_manager.get_value(APP_ID_PROPERTY)

        return """<html>
                       <head>
                            <script>
                                function recalculate_height(){
                                    var ifr = document.getElementById('weblab_iframe');
                                    if(ifr.contentWindow.document.body != null){
                                        var h = ifr.contentWindow.document.body.scrollHeight;
                                        ifr.height = h;
                                    }
                                    setTimeout("recalculate_height();", 200);
                                }
                            </script>
                       </head>
                    <body>
                         <div id="fb-root">
                            <iframe width="100%%" frameborder="0" height="100%%" id="weblab_iframe" scrolling="yes" src="%s?session_id=%s&facebook=true&mobile=no&%s">
                            </ifame>
                         </div>
                        <script src="http://connect.facebook.net/en_US/all.js"></script>
                        <script>
                            FB.init({
                                appId  : "%s",
                                channelUrl  : 'https://www.weblab.deusto.es/weblab/channel.html'  // custom channel
                            });
                                setTimeout("recalculate_height();", 200);
                        </script>

                    </body>
                </html>
            """ % (client_address, '%s;%s' % (session_id.id, self.weblab_cookie), locale, facebook_app_id)

    def _handle_linking_accounts(self, signed_request):
        username = self.get_argument('username')
        password = self.get_argument('password')
        try:
            session_id = self.server.grant_external_credentials(username, password, 'FACEBOOK', signed_request)
        except LoginExceptions.InvalidCredentialsException:
            return "Invalid username or password!"
        else:
            return self._show_weblab(session_id, signed_request)

    def _handle_creating_accounts(self, signed_request):
        try:
            session_id = self.server.create_external_user('FACEBOOK', signed_request)
        except LoginExceptions.InvalidCredentialsException:
            return "Invalid username or password!"
        else:
            return self._show_weblab(session_id, signed_request)


    def _handle_unauthenticated_clients(self, signed_request):
        if self.get_argument('op','').lower() == 'create':
            return self._handle_creating_accounts(signed_request)
        if self.get_argument('op','').lower() == 'link':
            return self._handle_linking_accounts(signed_request)

        link_uri = self.uri + '?op=link'
        create_uri = self.uri + '?op=create'

        return """<html>
                <head>
                    <style>
                        body{
                            font: 14px normal "Lucida Grande", Arial;
                        }
                    </style>
                </head>
                <body>
                <center><img src="../../../logo.png"></center> 
                <p>It seems that your Facebook account has not been linked with a WebLab-Deusto account, or that you don't have a WebLab-Deusto account.</p>
                <br>
                <h2>Already have a WebLab-Deusto account?</h2>
                <p>If you have an account in the University of Deusto and you'd like to link your facebook account (highly recommendable), fill your credentials and press <i>Link</i> to link both accounts so as to use WebLab-Deusto. Doing this you will be able to use the same experiments you use in WebLab-Deusto from Facebook.</p>
                <center><form method="POST" action="%(LINK_URI)s">
                Username: <input type="text" name="username"></input><br/>
                Password: <input type="password" name="password"></input><br/>
                <input type="hidden" name="signed_request" value="%(SIGNED_REQUEST)s"></input>
                <input type="submit" value="Link"></input>
                </form></center>
                <br>
                <h2>New to WebLab-Deusto?</h2>
                <p><a href="http://www.weblab.deusto.es/">WebLab-Deusto</a> is an <a href="http://code.google.com/p/weblabdeusto/">Open Source</a> Remote Laboratory developed in the <a href="http://www.deusto.es/">University of Deusto</a>. Students access experiments physically located in the University from any point in the Internet, just as they would in a hands-on-lab session.
                <p>If you don't have a WebLab-Deusto account but you'd like to see it, click on <i>Create</i> and you'll have a new account with permissions to the default demos we have deployed, with safe experiments that we know that final users will not be able to break.</p>
                <center> <form method="POST" action="%(CREATE_URI)s">
                    <input type="hidden" name="signed_request" value="%(SIGNED_REQUEST)s"></input>
                    <input type="submit" value="Create"></input>
                </form> </center>
            </body></html>""" % {
                        'LINK_URI' : link_uri,
                        'CREATE_URI' : create_uri,
                        'SIGNED_REQUEST' : signed_request,
                    }
