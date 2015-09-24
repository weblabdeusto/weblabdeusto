#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import urllib2
from StringIO import StringIO


HTTP_OK = "HTTP_OK"
HTTP_URL_ERROR = "HTTP_URL_ERROR"
HTTP_BAD_CONTENT = "HTTP_BAD_CONTENT"

expected_action = HTTP_OK

def reset():
    global expected_action
    expected_action = HTTP_OK

def urlopen(url):
    if expected_action == HTTP_OK:
        return HttpResponseOk()
    elif expected_action == HTTP_URL_ERROR:
        raise urllib2.URLError("")
    elif expected_action == HTTP_BAD_CONTENT:
        return HttpResponseBadContent()
    else:
        raise RuntimeError("Unknown value for return_value in fake urlopen()")


class HttpResponseOk(urllib2.addinfourl):

    def __init__(self):
        urllib2.addinfourl.__init__(self, StringIO(""), {}, "")
        self.headers['content-type'] = 'image/jpg'


class HttpResponseBadContent(urllib2.addinfourl):

    def __init__(self):
        urllib2.addinfourl.__init__(self, StringIO(""), {}, "")
        self.headers['content-type'] = 'application/xml'
