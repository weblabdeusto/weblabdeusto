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

import xmlrpclib
import weakref
import traceback
import base64
import urllib2

try:
    import json as json_module # Python >= 2.6
    json = json_module
except ImportError:
    import simplejson as json_mod
    json = json_mod

from facebook_config import _APP_ID, _CANVAS_URL, _CLIENT_ADDRESS, _FACEBOOK_APP

_AUTH_URL = "http://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=email" % (_APP_ID, urllib2.quote(_CANVAS_URL))

REQUEST_FIELD = 'signed_request'
WEBLAB_WS_URL  = 'http://localhost/weblab/login/xmlrpc/'

class _CookiesTransport(xmlrpclib.Transport):
    def send_user_agent(self, connection):
        _CookiesTransport.__bases__[0].send_user_agent(self, connection)
        if hasattr(self, '_sessid_cookie'):
            connection.putheader("Cookie",self._sessid_cookie)
        self.__connection = connection

    def _parse_response(self, *args, **kwargs):
        for header, value in self.__connection.headers.items():
            if header.lower() == 'set-cookie':
                real_value = value.split(';')[0]
                self._sessid_cookie = real_value
                server = self._real_server()
                if server is not None:
                    server.weblabsessionid = real_value
        return _CookiesTransport.__bases__[0]._parse_response(self, *args, **kwargs)


def _create_weblab_client(url, req):
    from mod_python.Cookie import get_cookie

    server = xmlrpclib.Server(url)
    transport = server._ServerProxy__transport
    transport.__class__  = _CookiesTransport
    transport._real_server = weakref.ref(server)

    cookie = get_cookie(req, "loginweblabsessionid")
    if cookie is not None:
        server._ServerProxy__transport._sessid_cookie = "loginweblabsessionid=%s" % cookie.value

    return server

def _handle_linking_accounts(req, kargs, signed_request):
    from mod_python import apache
    username = kargs['username']
    password = kargs['password']
    weblab_client = _create_weblab_client(WEBLAB_WS_URL, req)
    try:
        session_id = weblab_client.grant_external_credentials(username, password, 'FACEBOOK', signed_request)
    except xmlrpclib.Fault, f:
        if f.faultCode == u'XMLRPC:Client.Authentication':
            return "Invalid username or password!"
        else:
            msg = str(f) + "\n" + traceback.format_exc()
            apache.log_error(msg)
            return "ERROR: There was an error on the server linking accounts. Contact the administrator"
    except Exception, e:
        msg = str(e) + "\n" + traceback.format_exc()
        apache.log_error(msg)
        return "ERROR: There was an error on the server linking accounts. Contact the administrator"
    else:
        return _show_weblab(session_id, weblab_client.weblabsessionid, signed_request)

def _handle_creating_accounts(req, kargs, signed_request):
    from mod_python import apache
    weblab_client = _create_weblab_client(WEBLAB_WS_URL, req)
    try:
        session_id = weblab_client.create_external_user('FACEBOOK', signed_request)
    except xmlrpclib.Fault, f:
        if f.faultCode == u'XMLRPC:Client.Authentication':
            return "Invalid username or password!"
        else:
            msg = str(f) + "\n" + traceback.format_exc()
            apache.log_error(msg)
            return "ERROR: There was an error on the server creating account: %s. Contact the administrator" % f
    except Exception, e:
        msg = str(e) + "\n" + traceback.format_exc()
        apache.log_error(msg)
        return "ERROR: There was an error on the server creating account: %s. Contact the administrator" % e
    else:
        return _show_weblab(session_id, weblab_client.weblabsessionid, signed_request)


def _handle_unauthenticated_clients(req, kargs, signed_request):
    from mod_python import apache

    if kargs.get('op','').lower() == 'create':
        return _handle_creating_accounts(req, kargs, signed_request)
    if kargs.get('op','').lower() == 'link':
        return _handle_linking_accounts(req, kargs, signed_request)

    link_uri = req.uri + '?op=link'
    create_uri = req.uri + '?op=create'

    return """<html>
            <head>
                <style>
                    body{
                        font: 14px normal "Lucida Grande", Arial;
                    }
                </style>
            </head>
            <body>
            <center><img src="../logo.png"></center> 
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
                    'SIGNED_REQUEST' : kargs['signed_request'],
                }

def _show_weblab(session_id, cookie_end, signed_request):
    payload = signed_request[signed_request.find('.') + 1:]
    payload = payload.replace('-','+').replace('_','/')
    payload = payload + "=="
    json_content = base64.decodestring(payload)
    data = json.loads(json_content)
    locale = ''
    if 'user' in data:
        if 'locale' in data['user']:
            locale = "&locale=%s" % data['user']['locale']

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
                        <iframe width="100%%" frameborder="0" height="100%%" id="weblab_iframe" scrolling="no" src="%s?session_id=%s&facebook=true&mobile=no&%s">
                        </iframe>
                     </div>
                    <script src="http://connect.facebook.net/en_US/all.js"></script>
                    <script>
                        FB.init({
                            appId  : %s,
                            channelUrl  : 'https://www.weblab.deusto.es/weblab/channel.html'  // custom channel
                        });
                            setTimeout("recalculate_height();", 200);
                    </script>

                </body>
            </html>
        """ % (_CLIENT_ADDRESS, '%s;%s' % (session_id['id'], cookie_end), locale, _APP_ID, _APP_ID)

def index(req, *args, **kargs): 
    if not req.form.has_key(REQUEST_FIELD):
        return "<html><body><script>top.location.href='%s';</script></body></html>" % _FACEBOOK_APP

    signed_request = kargs['signed_request']

    payload = signed_request[signed_request.find('.') + 1:]
    payload = payload.replace('-','+').replace('_','/')
    payload = payload + "=="
    json_content = base64.decodestring(payload)
    data = json.loads(json_content)
    if 'user_id' not in data:
        return "<html><body><script>top.location.href='%s';</script></body></html>" % _AUTH_URL

    from mod_python import apache

    weblab_client = _create_weblab_client(WEBLAB_WS_URL, req)
    try:
        session_id = weblab_client.login_based_on_other_credentials('FACEBOOK', signed_request)
    except xmlrpclib.Fault, f:
        if f.faultCode == u'XMLRPC:Client.Authentication' or f.faultCode == u'XMLRPC:Client.InvalidCredentials':
            return _handle_unauthenticated_clients(req, kargs, signed_request)
        else:
            msg = str(f) + "\n" + traceback.format_exc()
            apache.log_error(msg)
            return "ERROR: There was a XML-RPC error on the server. Contact the administrator"
    except Exception, e:
        msg = str(e) + "\n" + traceback.format_exc()
        apache.log_error(msg)
        return "ERROR: There was an error on the server. Contact the administrator"

    return _show_weblab(session_id, weblab_client.weblabsessionid, signed_request)

