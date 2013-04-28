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
    def create_user_auth(name, configuration):
        if name == LdapUserAuth.NAME:
            return LdapUserAuth(configuration)
        elif name == TrustedIpAddressesUserAuth.NAME:
            return TrustedIpAddressesUserAuth(configuration)
        elif name == TrustedIpAddressesUserAuth.NAME:
            return TrustedIpAddressesUserAuth(configuration)
        elif name == FacebookUserAuth.NAME:
            return FacebookUserAuth(configuration)
        elif name == OpenIDUserAuth.NAME:
            return OpenIDUserAuth(configuration)
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

    def __init__(self, configuration):
        self.hashed_password = configuration

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

    def __init__(self, configuration):
        mo = re.match(LdapUserAuth.REGEX, configuration)
        if mo is None:
            raise DbErrors.DbInvalidUserAuthConfigurationError(
                "Invalid configuration: %s" % configuration
            )
        ldap_uri, domain, base = mo.groups()

        self.ldap_uri = ldap_uri
        self.domain = domain
        self.base = base
        self.configuration = configuration

    @property
    def name(self):
        return LdapUserAuth.NAME

    def __str__(self):
        return "LdapUserAuth(domain=%r, ldap_uri=%r, base=%r)" % (self.domain, self.ldap_uri, self.base)

    def __repr__(self):
        return "LdapUserAuth(configuration=%r)" % (self.configuration)

class TrustedIpAddressesUserAuth(SimpleAuthnUserAuth):
    NAME = 'TRUSTED-IP-ADDRESSES'
    def __init__(self, configuration):
        self.addresses = [ ip.strip() for ip in configuration.split(',') ]

    @property
    def name(self):
        return TrustedIpAddressesUserAuth.NAME

    def __repr__(self):
        return "TrustedIpAddressesUserAuth(addresses=%r)" % self.addresses

    def __repr__(self):
        return "TrustedIpAddressesUserAuth(configuration=%r)" % self.addresses

class FacebookUserAuth(WebProtocolUserAuth):

    NAME = 'FACEBOOK'

    def __init__(self, configuration):
        self.configuration = configuration

    def __str__(self):
        return "FacebookUserAuth(user_id=%r)" % self.configuration

    @property
    def name(self):
        return FacebookUserAuth.NAME

    def __repr__(self):
        return "FacebookUserAuth(configuration=%r)" % self.configuration

class OpenIDUserAuth(WebProtocolUserAuth):

    NAME = 'OPENID'

    def __init__(self, configuration):
        self.configuration = configuration

    def __str__(self):
        return "OpenIDUserAuth(identifier=%r)" % self.configuration

    @property
    def name(self):
        return OpenIDUserAuth.NAME

    def __repr__(self):
        return "OpenIDUserAuth(configuration=%r)" % self.configuration


