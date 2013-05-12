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
# Author: Pablo Orduña <pablo@ordunya.com>
#

import thread

_contexts = {}

def _get_identifier():
    return thread.get_ident()

def get_context():
    global _contexts
    return _contexts.get(_get_identifier()) or NullRemoteFacadeContext()

def create_context(server, client_address, headers):
    global _contexts
    _contexts[_get_identifier()] = RemoteFacadeContext(server, client_address, headers, None, None)

def delete_context():
    global _contexts
    _contexts.pop(_get_identifier())

class RemoteFacadeContext(object):
    def __init__(self, server, client_address, headers, route, session_id):
        self._server         = server
        self._client_address = client_address
        self.headers         = headers
        self.route           = route
        self.session_id      = session_id

    def get_ip_address(self):
        try:
            return self.headers.get('X-Forwarded-For') or ('<unknown client. retrieved from %s>' % self._client_address[0])
        except KeyError:
            return '<unknown client. retrieved from %s>' % self._client_address[0]

    @property
    def ip_address(self):
        return self.get_ip_address()

    def get_user_agent(self):
        try:
            return self.headers.get('User-Agent') or '<unknown>'
        except KeyError:
            return '<unknown>'

    @property
    def user_agent(self):
        return self.get_user_agent()

    def get_referer(self):
        try:
            return self.headers.get('Referer') or ''
        except KeyError:
            return ''

    @property
    def referer(self):
        return self.get_referer()

    def get_locale(self):
        try:
            return self.headers.get('weblabdeusto-locale') or ''
        except KeyError:
            return ''
    @property
    def locale(self):
        return self.get_locale()

    def is_mobile(self):
        if self.headers.get('weblabdeusto-client') == 'weblabdeusto-web-mobile':
            return True
        referer = self.get_referer()
        return referer.find('mobile=true') >= 0 or referer.find('mobile=yes') >= 0

    def is_facebook(self):
        referer = self.get_referer()
        return referer.find('facebook=true') >= 0 or referer.find('facebook=yes') >= 0


class NullRemoteFacadeContext(RemoteFacadeContext):
    def __init__(self):
        super(NullRemoteFacadeContext, self).__init__('', ('', 80), {}, None, None)

