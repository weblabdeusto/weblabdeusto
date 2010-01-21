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

USERNAME_FIELD = 'username'
WEBLAB_WS_URL  = 'http://localhost/weblab/xmlrpc/'

def _create_weblab_client(url):
    return xmlrpclib.Server(url)

def index(req, *args, **kargs):
    if not req.form.has_key(USERNAME_FIELD):
        return "ERROR: Missing username field"

    from mod_python import apache

    weblab_client = _create_weblab_client(WEBLAB_WS_URL)
    try:
        session_id = weblab_client.login_based_on_client_address(str(req.form[USERNAME_FIELD]), req.get_remote_host())
    except xmlrpclib.Fault, f:
        if f.faultCode == u'XMLRPC:Client.Authentication':
            return "Error: incorrect login or password"
        else:
            msg = str(f) + "\n" + traceback.format_exc()
            apache.log_error(msg)
            return "ERROR: There was an error on the server. Contact the administrator"
    except Exception, e:
        msg = str(e) + "\n" + traceback.format_exc()
        apache.log_error(msg)
        return "ERROR: There was an error on the server. Contact the administrator"
    return session_id['id']
