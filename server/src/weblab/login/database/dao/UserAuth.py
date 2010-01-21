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

import re

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

class UserAuth(object):
    @staticmethod
    def create_user_auth(name, configuration):
        if name == LdapUserAuth.NAME:
            return LdapUserAuth(configuration)
        elif name == TrustedIpAddressesUserAuth.NAME:
            return TrustedIpAddressesUserAuth(configuration)
        else:
            raise DbExceptions.DbUnsupportedUserAuth("UserAuth %s not supported" % name)

class LdapUserAuth(object):
    NAME = 'LDAP'
    REGEX = 'domain=([a-zA-Z0-9\._-]+);ldap_uri=(ldaps?://[a-zA-Z0-9\./_-]+)'
    def __init__(self, configuration):
        mo = re.match(LdapUserAuth.REGEX, configuration)
        if mo is None:
            raise DbExceptions.DbInvalidUserAuthConfigurationException(
                "Invalid configuration: %s" % configuration
            )
        domain, ldap_uri = mo.groups()

        self.domain = domain
        self.ldap_uri = ldap_uri

    @property
    def name(self):
        return LdapUserAuth.NAME

    def __repr__(self):
        return "<LdapUserAuth domain='%s' ldap_uri='%s'/>" % (self.domain, self.ldap_uri)

class TrustedIpAddressesUserAuth(object):
    NAME = 'TRUSTED-IP-ADDRESSES'
    def __init__(self, configuration):
        self.addresses = [ ip.strip() for ip in configuration.split(',') ]

    @property
    def name(self):
        return TrustedIpAddressesUserAuth.NAME

    def __repr__(self):
        return "<TrustedIpAddressesUserAuth addresses='%s'/>" % self.addresses

