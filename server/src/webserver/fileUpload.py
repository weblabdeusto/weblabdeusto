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

# Configuration required in mod_python:
# 
# <Directory "/var/www/weblab">
#        AddHandler python-program .py
#        PythonHandler mod_python.publisher
#        PythonDebug on
# </Directory>
#

import xmlrpclib
import sys

if sys.version_info[:2] == (2,5):
    from types import InstanceType
    # This code is copied from python2.6 xmlrpclib
    def _new__dump(self, value, write):
        try:
            f = self.dispatch[type(value)]
        except KeyError:
            # check if this object can be marshalled as a structure
            try:
                value.__dict__
            except:
                raise TypeError, "cannot marshal %s objects" % type(value)
            # check if this class is a sub-class of a basic type,
            # because we don't know how to marshal these types
            # (e.g. a string sub-class)
            for type_ in type(value).__mro__:
                if type_ in self.dispatch.keys():
                    raise TypeError, "cannot marshal %s objects" % type(value)
            f = self.dispatch[InstanceType]
        f(self, value, write)

    import xmlrpclib
    xmlrpclib.Marshaller._Marshaller__dump = _new__dump

import base64

WEBLAB_WS_URL  = 'http://localhost/weblab/xmlrpc/'
WEBLAB_GENERAL_EXCEPTION_CODE = 'Server.WebLab'
PYTHON_GENERAL_EXCEPTION_CODE = 'Server.Python'

FILE_SENT_ATTR    = 'file_sent'
FILE_INFO_ATTR    = 'file_info'
SESSION_ID_ATTR   = 'session_id'

BASE_HTML_TEMPLATE="""<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>WebLab upload</title>
    </head>
    <body>%(MESSAGE)s</body>
</html>
"""

SUCCESS_HTML_TEMPLATE = BASE_HTML_TEMPLATE % {
		"MESSAGE" : "SUCCESS@%(RESULT)s"
	}

FAULT_HTML_TEMPLATE = BASE_HTML_TEMPLATE % {
		"MESSAGE" : "ERROR@%(THE_FAULT_CODE)s@%(THE_FAULT_MESSAGE)s"
	}

def _check_attributes(req):
    missing_attributes = []
    if not req.form.has_key(FILE_SENT_ATTR):
        missing_attributes.append(FILE_SENT_ATTR)
    if not req.form.has_key(FILE_INFO_ATTR):
        missing_attributes.append(FILE_INFO_ATTR)
    if not req.form.has_key(SESSION_ID_ATTR):
        missing_attributes.append(SESSION_ID_ATTR)
    if len(missing_attributes) > 0:
        fault_message = 'Missing attributes: %s' % missing_attributes
        return FAULT_HTML_TEMPLATE % {
                        'THE_FAULT_CODE'    : WEBLAB_GENERAL_EXCEPTION_CODE,
                        'THE_FAULT_MESSAGE' : fault_message
                    }
    else:
        return None

class _CookiesTransport(xmlrpclib.Transport):
    def send_user_agent(self, connection):
        _CookiesTransport.__bases__[0].send_user_agent(self, connection)
        if hasattr(self, '_sessid_cookie'):
            connection.putheader("Cookie", self._sessid_cookie)

def _create_weblab_client(url, session_id):
    server = xmlrpclib.Server(url, allow_none = True)
    transport = server._ServerProxy__transport
    transport.__class__  = _CookiesTransport
    transport._sessid_cookie = session_id
    return server

class SessionId(object):
    def __init__(self, session_id):
        self.id = session_id
    def __cmp__(self, other):
        if isinstance(other, SessionId):
            return cmp(self.id, other.id)
        else:
            return 1
    def __repr__(self):
        return "<SessionId id='%s'/>" % self.id

def index(req, *args, **kargs):
    error_message = _check_attributes(req)
    if error_message is not None:
        return error_message

    cookie = req.headers_in.get("Cookie", 'foo=bar')

    form_file_content = req.form[FILE_SENT_ATTR].file.read()
    form_session_id   = str(req.form[SESSION_ID_ATTR])
    form_file_info    = str(req.form[FILE_INFO_ATTR])

    file_content = base64.encodestring(form_file_content)
    weblab_client = _create_weblab_client(WEBLAB_WS_URL, cookie)

    session_id = SessionId(form_session_id)

    try:
        result = weblab_client.send_file(
                session_id,
                file_content,
                form_file_info
            )
    except xmlrpclib.Fault, f:
        return FAULT_HTML_TEMPLATE % {
                'THE_FAULT_CODE' : f.faultCode,
                'THE_FAULT_MESSAGE' : f.faultString
            }

    except Exception, e:
        return FAULT_HTML_TEMPLATE % {
                'THE_FAULT_CODE' : PYTHON_GENERAL_EXCEPTION_CODE,
                'THE_FAULT_MESSAGE' : e.args[0]
            }
    else:
        return SUCCESS_HTML_TEMPLATE % {
                'RESULT' : result['commandstring']
            }

