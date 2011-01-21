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

def _create_weblab_client(url):
    return xmlrpclib.Server(url)

def _handle_linking_accounts(req, kargs, signed_request):
    from mod_python import apache
    username = kargs['username']
    password = kargs['password']
    weblab_client = _create_weblab_client(WEBLAB_WS_URL)
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
        return _show_weblab(session_id)

def _handle_creating_accounts(req, kargs, signed_request):
    from mod_python import apache
    weblab_client = _create_weblab_client(WEBLAB_WS_URL)
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
        return _show_weblab(session_id)


def _handle_unauthenticated_clients(req, kargs, signed_request):
    from mod_python import apache

    if kargs.get('op','').lower() == 'create':
        return _handle_creating_accounts(req, kargs, signed_request)
    if kargs.get('op','').lower() == 'link':
        return _handle_linking_accounts(req, kargs, signed_request)

    link_uri = req.uri + '?op=link'
    create_uri = req.uri + '?op=link'

    return """<html><body>
            <p>It seems that your Facebook account has not been linked with a WebLab-Deusto account, or that you don't have a WebLab-Deusto account.</p>
            <p>If you'd like to link your existing WebLab-Deusto account, fill your credentials and press Log in</p>
            <center><form method="POST" action="%(LINK_URI)s">
            Username: <input type="text" name="username"></input><br/>
            Password: <input type="password" name="password"></input><br/>
            <input type="hidden" name="signed_request" value="%(SIGNED_REQUEST)s"></input>
            <input type="submit" value="Link"></input>
            </form></center>
<!--            <p>If you don't have a WebLab-Deusto account but you'd like to have one, just press <a href="%(CREATE_URI)s">here</a></p> -->
        </body></html>""" % {
                    'LINK_URI' : link_uri,
                    'CREATE_URI' : create_uri,
                    'SIGNED_REQUEST' : kargs['signed_request'],
                }

def _show_weblab(session_id):
    return """<html>
                   <head>
                        <script>
                            function recalculate_height(){
                                var ifr = document.getElementById('weblab_iframe');
                                var h = ifr.contentWindow.document.body.scrollHeight;
                                ifr.height = h;
                                setTimeout("recalculate_height();", 200);
                            }
                        </script>
                   </head>
                <body>
                     <div id="fb-root">
                        <iframe width="100%%" frameborder="0" height="100%%" id="weblab_iframe" scrolling="no" src="%s?session_id=%s">
                        </iframe>
                     </div>
                    <script>
                        window.fbAsyncInit = function() {
                                FB.init({appId: '%s', status: true, cookie: true,
                                xfbml: true});
                                FB.Canvas.setAutoResize();
                            };
                        (function() {
                            var e = document.createElement('script'); 
                            e.async = true;
                            e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
                            document.getElementById('fb-root').appendChild(e);
                        }());
                        setTimeout("recalculate_height();", 200);
                    </script>
                </body>
            </html>
        """ % (_CLIENT_ADDRESS, session_id['id'],_APP_ID)

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

    weblab_client = _create_weblab_client(WEBLAB_WS_URL)
    try:
        session_id = weblab_client.login_based_on_other_credentials('FACEBOOK', signed_request)
    except xmlrpclib.Fault, f:
        if f.faultCode == u'XMLRPC:Client.Authentication' or f.faultCode == u'XMLRPC:Client.InvalidCredentials':
            return _handle_unauthenticated_clients(req, kargs, signed_request)
        else:
            msg = str(f) + "\n" + traceback.format_exc()
            apache.log_error(msg)
            return "ERROR: There was an error on the server. Contact the administrator"
    except Exception, e:
        msg = str(e) + "\n" + traceback.format_exc()
        apache.log_error(msg)
        return "ERROR: There was an error on the server. Contact the administrator"

    return _show_weblab(session_id)

