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

import thread

_contexts = {}

def _get_identifier():
    return thread.get_ident()

def get_context():
    global _contexts
    return _contexts.get(_get_identifier()) or NullRemoteFacadeContext()

def create_context(server, headers):
    global _contexts
    _contexts[_get_identifier()] = RemoteFacadeContext(server, headers, None)

def delete_context():
    global _contexts
    _contexts.pop(_get_identifier())

class RemoteFacadeContext(object):
    def __init__(self, server, headers, route):
        self._server  = server
        self._headers = headers
        self.route    = route

    def get_ip_address(self):
        try:
            return self._headers.get('X-Forwarded-For') or '<unknown client>'
        except KeyError:
            return '<unknown client>'

    def get_user_agent(self):
        try:
            return self._headers.get('User-Agent') or '<unknown>'
        except KeyError:
            return '<unknown>'

    def get_referer(self):
        try:
            return self._headers.get('Referer') or ''
        except KeyError:
            return ''

    def is_mobile(self):
        referer = self.get_referer()
        return referer.find('mobile=true') >= 0 or referer.find('mobile=yes') >= 0

    def is_facebook(self):
        referer = self.get_referer()
        return referer.find('facebook=true') >= 0 or referer.find('facebook=yes') >= 0


class NullRemoteFacadeContext(RemoteFacadeContext):
    def __init__(self):
        super(NullRemoteFacadeContext, self).__init__('', {}, None)

