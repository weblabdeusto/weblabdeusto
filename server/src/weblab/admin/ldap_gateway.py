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
from __future__ import print_function, unicode_literals


import sys

import ldap


class LdapGateway(object):

    def __init__(self, uri, domain, base, auth_username, auth_password):
        super(LdapGateway, self).__init__()
        self.uri = uri
        self.domain = domain
        self.base = base
        self.auth_username = auth_username
        self.auth_password = auth_password
        self.connection = ldap.initialize(uri)
        # We test the connection to check the credentials
        #self._bind()
        #self._unbind()

    def _parse_result_set(self, result_set, user_login):
        user_map = result_set[0][1]
        return { "login"    : user_login,
                 "full_name": "%s %s" % (user_map['givenName'][0], user_map['sn'][0]),
                 "email"    : user_map['mail'][0] }

    def _bind(self):
        username = '%(USERNAME)s@%(DOMAIN)s' % {
                                            'USERNAME' : self.auth_username,
                                            'DOMAIN'   : self.domain
                                      }
        self.connection.simple_bind_s(username, self.auth_password)

    def _unbind(self):
        self.connection.unbind()

    def get_users(self, user_logins):
        users = []
        self._bind()
        for user_login in user_logins:
            result_set = self.connection.search_s(
                                self.base,                          # base
                                ldap.SCOPE_SUBTREE,                 # scope :-S
                                '(sAMAccountName=%s)' % user_login, # filter
                                [str("givenName"),str("sn"),str("mail")]           # retrieved attributes (is this ok?)
                         )
            if len(result_set) < 1:
                print("User '%s' not found" % user_login, file=sys.stderr)
            elif len(result_set) > 1:
                print("Invalid state: too many users found for username %s" % user_login, file=sys.stderr)
                users.append(self._parse_result_set(result_set, user_login))
            else:
                users.append(self._parse_result_set(result_set, user_login))
        self._unbind()
        return users
