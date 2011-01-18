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

from facebook_config import _APP_ID, _CANVAS_URL, _CLIENT_ADDRESS

_AUTH_URL = "http://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s" % (_APP_ID, urllib2.quote(_CANVAS_URL))

REQUEST_FIELD = 'signed_request'
WEBLAB_WS_URL  = 'http://localhost/weblab/login/xmlrpc/'

def _create_weblab_client(url):
    return xmlrpclib.Server(url)

def index(req, *args, **kargs):
    if not req.form.has_key(REQUEST_FIELD):
        return "ERROR: Missing request field"

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
        if f.faultCode == u'XMLRPC:Client.Authentication':
            return "Error: incorrect credentials"
        else:
            msg = str(f) + "\n" + traceback.format_exc()
            apache.log_error(msg)
            return "ERROR: There was an error on the server. Contact the administrator"
    except Exception, e:
        msg = str(e) + "\n" + traceback.format_exc()
        apache.log_error(msg)
        return "ERROR: There was an error on the server. Contact the administrator"

    return """<html><body><iframe width="100%%" height="100%%" frameborder="0" scrolling="no" src="%s?session_id=%s"></body></html>""" % (_CLIENT_ADDRESS, session_id['id'])
