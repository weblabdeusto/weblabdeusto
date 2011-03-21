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
        """ 
        Called whenever an XMLRPC request is sent, we will extend the functionality
        of its base class to also append a Cookie HTTP header with our loginweblabsessionid
        cookie, if it is present.
        """
        _CookiesTransport.__bases__[0].send_user_agent(self, connection)
        if hasattr(self, '_sessid_cookie'):
            connection.putheader("Cookie",self._sessid_cookie)
        self.__connection = connection

    def _parse_response(self, *args, **kwargs):
        """
        Called whenever the response of an XMLRPC request arrives, we will seek the 
        set-cookie http header. If found, we assume that it is our weblabsessionid cookie
        and store it locally as our weblabsessionid.
        """
        for header, value in self.__connection.headers.items():
            if header.lower() == 'set-cookie':
                real_value = value.split(';')[0]
                self._sessid_cookie = real_value
                server = self._real_server()
                if server is not None:
                    server.weblabsessionid = real_value
        return _CookiesTransport.__bases__[0]._parse_response(self, *args, **kwargs)


def _create_weblab_client(url, req):
    """ Create the weblab xmlrpc client to send the login request """
    
    from mod_python.Cookie import get_cookie
    server = xmlrpclib.Server(url)
    
    # We need to override certain internal objects to be able to handle cookies 
    # on the XMLRPC requests.
    transport = server._ServerProxy__transport
    transport.__class__  = _CookiesTransport
    transport._real_server = weakref.ref(server)

    # Retrieve the loginweblabessionid cookie which was sent to this script.
    # Save it on our transport so that it can forward that cookie when the
    # XMLRPC request is carried out.
    cookie = get_cookie(req, "loginweblabsessionid")
    if cookie is not None:
        server._ServerProxy__transport._sessid_cookie = "loginweblabsessionid=%s" % cookie.value

    return server

    
def index(req, *args, **kargs):
    if not req.form.has_key(USERNAME_FIELD):
        return "ERROR: Missing username field"

    from mod_python import apache

    weblab_client = _create_weblab_client(WEBLAB_WS_URL, req)
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
