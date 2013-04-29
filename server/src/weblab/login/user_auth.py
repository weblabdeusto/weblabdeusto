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

import sys
import hashlib
import weblab.data.client_address as ClientAddress
from abc import ABCMeta, abstractmethod

import weblab.db.exc as DbErrors
try:
    import ldap
except ImportError:
    LDAP_AVAILABLE = False
else:
    LDAP_AVAILABLE = True

import voodoo.log as log
import weblab.login.exc as LoginErrors

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
    
    @abstractmethod
    def authenticate(self, login, password):
        """ Provided the login and a password (or credential), check that 
        the user is who claims to be and return True (if authenticated) or 
        False (if failed to authenticate)"""

class WebProtocolUserAuth(UserAuth):
    def is_simple_authn(self):
        return False


###########################################################################
# 
#    Database based (storing hashed password in the database).
# 


class WebLabDbUserAuth(SimpleAuthnUserAuth):

    NAME = 'DB'

    def __init__(self, auth_configuration, user_auth_configuration):
        self.hashed_password = user_auth_configuration

    @property
    def name(self):
        return WebLabDbUserAuth.NAME

    def authenticate(self, login, password):
        #Now, user_password is the value stored in the database
        #
        #The format is: random_chars{algorithm}hashed_password
        #
        #random_characters will be, for example, axjl
        #algorithm will be md5 or sha (or sha1), or in the future, other hash algorithms
        #hashed_password will be the hash of random_chars + passwd, using "algorithm" algorithm
        #
        #For example:
        #aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474
        #would be the stored password for "password", since
        #the sha hash of "aaaapassword" is a7761...
        #
        REGEX = "([a-zA-Z0-9]*){([a-zA-Z0-9_-]+)}([a-fA-F0-9]+)"
        mo = re.match(REGEX, self.hashed_password)
        if mo is None:
            raise DbErrors.DbInvalidPasswordFormatError( "Invalid password format" )
        first_chars, algorithm, hashed_passwd = mo.groups()

        if algorithm == 'sha':
            algorithm = 'sha1' #TODO

        try:
            hashobj = hashlib.new(algorithm)
        except Exception:
            raise DbErrors.DbHashAlgorithmNotFoundError( "Algorithm %s not found" % algorithm )

        hashobj.update((first_chars + password).encode())
        return hashobj.hexdigest() == hashed_passwd

    def __str__(self):
        return "WebLabDbUserAuth(hashed_password=%r)" % self.hashed_password

    def __repr__(self):
        return "WebLabDbUserAuth(configuration=%r)" % self.hashed_password

#######################################################################
# 
#        LDAP
# 

# TODO: no test actually test the real ldap module. The problem is
# requiring a LDAP server in the integration machine (in our integration
# machine it's not a problem, but running those test in "any computer"
# might be a bigger problem)

if LDAP_AVAILABLE:
    class _LdapProvider(object):
        def __init__(self):
            self.ldap_module = ldap
        def get_module(self):
            return self.ldap_module

    _ldap_provider = _LdapProvider()


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

    def authenticate(self, login, password):
        if not LDAP_AVAILABLE:
            msg = "The optional library 'ldap' is not available. The users trying to be authenticated with LDAP will not be able to do so. %s tried to do it. " % login
            print >> sys.stderr, msg
            log.log(self, log.level.Error, msg)
            return False

        password = str(password)
        ldap_module = _ldap_provider.get_module()
        try:
            ldapobj = ldap_module.initialize(
                self.ldap_uri
            )
        except Exception as e:
            raise LoginErrors.LdapInitializingError(
                "Exception initializing the LDAP module: %s" % e
            )

        dn = "%s@%s" % (login, self.domain)
        pw = password

        try:
            ldapobj.simple_bind_s(dn, pw)
        except ldap.INVALID_CREDENTIALS as e:
            return False
        except Exception as e:
            raise LoginErrors.LdapBindingError(
                "Exception binding to the server: %s" % e
            )
        else:
            ldapobj.unbind_s()
            return True


    @property
    def name(self):
        return LdapUserAuth.NAME

    def __str__(self):
        return "LdapUserAuth(domain=%r, ldap_uri=%r, base=%r)" % (self.domain, self.ldap_uri, self.base)

    def __repr__(self):
        return "LdapUserAuth(configuration=%r)" % (self.auth_configuration)

#######################################################################
# 
#        Trusted Ip addresses
# 


class TrustedIpAddressesUserAuth(SimpleAuthnUserAuth):
    NAME = 'TRUSTED-IP-ADDRESSES'
    def __init__(self, auth_configuration, user_auth_configuration):
        self.addresses = [ ip.strip() for ip in auth_configuration.split(',') ]

    def authenticate(self, login, password):
        if not isinstance(password, ClientAddress.ClientAddress):
            return False
        client_address = password.client_address
        return client_address in self.addresses

    @property
    def name(self):
        return TrustedIpAddressesUserAuth.NAME

    def __repr__(self):
        return "TrustedIpAddressesUserAuth(configuration=%r)" % self.addresses


#######################################################################
# 
#        Facebook
# 


class FacebookUserAuth(WebProtocolUserAuth):

    NAME = 'FACEBOOK'

    def __init__(self, auth_configuration, user_auth_configuration):
        self.user_id = user_auth_configuration

    @property
    def name(self):
        return FacebookUserAuth.NAME

    def __repr__(self):
        return "FacebookUserAuth(user_id=%r)" % self.user_id


#######################################################################
# 
#        OpenID
# 

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

