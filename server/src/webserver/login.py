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

USERNAME_FIELD = 'username'
WEBLAB_WS_URL  = 'http://localhost/weblab/xmlrpc/'

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


def _create_weblab_client(url):
    server = xmlrpclib.Server(url)
    transport = server._ServerProxy__transport
    transport.__class__  = _CookiesTransport
    transport._real_server = weakref.ref(server)
    return server

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
    return '%s;%s' % (session_id['id'], weblab_client.weblabsessionid)
