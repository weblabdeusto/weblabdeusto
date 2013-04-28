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

import re

from abc import ABCMeta, abstractmethod

import weblab.db.exc as DbErrors

class UserAuth(object):

    __metaclass__ = ABCMeta

    @staticmethod
    def create_user_auth(name, auth_configuration, user_auth_configuration):
        if name == LdapUserAuth.NAME:
            return LdapUserAuth(auth_configuration, user_auth_configuration)
        elif name == WebLabDbUserAuth.NAME:
            return WebLabDbUserAuth(auth_configuration, user_auth_configuration)
        elif name == TrustedIpAddressesUserAuth.NAME:
            return TrustedIpAddressesUserAuth(auth_configuration, user_auth_configuration)
        elif name == FacebookUserAuth.NAME:
            return FacebookUserAuth(auth_configuration, user_auth_configuration)
        elif name == OpenIDUserAuth.NAME:
            return OpenIDUserAuth(auth_configuration, user_auth_configuration)
        else:
            raise DbErrors.DbUnsupportedUserAuth("UserAuth %s not supported" % name)

    @abstractmethod
    def is_simple_authn(self):
        """ Is the current system using a simple interface or it requires something external (e.g., Facebook or OpenID)? """


class SimpleAuthnUserAuth(UserAuth):
    def is_simple_authn(self):
        return True

class WebProtocolUserAuth(UserAuth):
    def is_simple_authn(self):
        return False

class WebLabDbUserAuth(SimpleAuthnUserAuth):

    NAME = 'DB'

    def __init__(self, auth_configuration, user_auth_configuration):
        self.hashed_password = user_auth_configuration

    @property
    def name(self):
        return WebLabDbUserAuth.NAME

    def __str__(self):
        return "WebLabDbUserAuth(hashed_password=%r)" % self.hashed_password

    def __repr__(self):
        return "WebLabDbUserAuth(configuration=%r)" % self.hashed_password

class LdapUserAuth(SimpleAuthnUserAuth):

    NAME = 'LDAP'
    REGEX = 'ldap_uri=(ldaps?://[a-zA-Z0-9\./_-]+);domain=([a-zA-Z0-9\._-]+);base=([a-zA-Z0-9=\,_-]+)'

    def __init__(self, auth_configuration, user_auth_configuration):
        mo = re.match(LdapUserAuth.REGEX, auth_configuration)
        if mo is None:
            raise DbErrors.DbInvalidUserAuthConfigurationError(
                "Invalid configuration: %s" % auth_configuration
            )
        ldap_uri, domain, base = mo.groups()

        self.ldap_uri = ldap_uri
        self.domain = domain
        self.base = base
        self.auth_configuration = auth_configuration

    @property
    def name(self):
        return LdapUserAuth.NAME

    def __str__(self):
        return "LdapUserAuth(domain=%r, ldap_uri=%r, base=%r)" % (self.domain, self.ldap_uri, self.base)

    def __repr__(self):
        return "LdapUserAuth(configuration=%r)" % (self.auth_configuration)

class TrustedIpAddressesUserAuth(SimpleAuthnUserAuth):
    NAME = 'TRUSTED-IP-ADDRESSES'
    def __init__(self, auth_configuration, user_auth_configuration):
        self.addresses = [ ip.strip() for ip in auth_configuration.split(',') ]

    @property
    def name(self):
        return TrustedIpAddressesUserAuth.NAME

    def __repr__(self):
        return "TrustedIpAddressesUserAuth(addresses=%r)" % self.addresses

    def __repr__(self):
        return "TrustedIpAddressesUserAuth(configuration=%r)" % self.addresses

class FacebookUserAuth(WebProtocolUserAuth):

    NAME = 'FACEBOOK'

    def __init__(self, auth_configuration, user_auth_configuration):
        self.user_id = user_auth_configuration

    @property
    def name(self):
        return FacebookUserAuth.NAME

    def __repr__(self):
        return "FacebookUserAuth(user_id=%r)" % self.user_id

class OpenIDUserAuth(WebProtocolUserAuth):

    NAME = 'OPENID'

    def __init__(self, auth_configuration, user_auth_configuration):
        self.user_auth_configuration = user_auth_configuration

    def __str__(self):
        return "OpenIDUserAuth(identifier=%r)" % self.user_auth_configuration

    @property
    def name(self):
        return OpenIDUserAuth.NAME

    def __repr__(self):
        return "OpenIDUserAuth(configuration=%r)" % self.user_auth_configuration

