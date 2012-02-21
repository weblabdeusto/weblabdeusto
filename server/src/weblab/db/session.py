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

class DatabaseSessionId(object):
    def __init__(self,valid):
        super(DatabaseSessionId,self).__init__()
        self.valid = valid

class ValidDatabaseSessionId(DatabaseSessionId):
    def __init__(self, username = None, role = ''):
        super(ValidDatabaseSessionId,self).__init__(True)
        self.role = role
        self.username = username

    def __repr__(self):
        return '<%(class_name)s> %(role_name)s@%(username)s' % {
                'class_name' : self.__class__,
                'role_name'  : self.role,
                'username'   : self.username
            }

class InvalidDatabaseSessionId(DatabaseSessionId):
    def __init__(self):
        super(InvalidDatabaseSessionId,self).__init__(False)

    def __repr__(self):
        return '<%(class_name)s> Invalid_session' % {
                    'class_name' : self.__class__
                }

class NotAuthenticatedSessionId(DatabaseSessionId):
    def __init__(self, username, role, user_auths):
        super(NotAuthenticatedSessionId, self).__init__(False)
        self.role       = role
        self.username   = username
        self.user_auths = user_auths

    def __repr__(self):
        return '<%(class_name)s> NotAuthenticated_session: %(role_name)s@%(username)s; %(user_auth)s' % {
                    'class_name' : self.__class__,
                    'role_name'  : self.role,
                    'username'   : self.username,
                    'user_auth'  : self.user_auths
                }

