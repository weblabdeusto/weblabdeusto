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
import hashlib
import sys
import weblab.db.exc as DbErrors
from abc import ABCMeta, abstractmethod
try:
    import ldap
except ImportError:
    LDAP_AVAILABLE = False
else:
    LDAP_AVAILABLE = True

import voodoo.log as log
import weblab.data.client_address as ClientAddress
import weblab.login.db.dao.user as UserAuth
import weblab.login.exc as LoginErrors

class LoginAuth(object):

    __metaclass__ = ABCMeta

    HANDLERS = ()

    @staticmethod
    def create(user_auth):
        for i in LoginAuth.HANDLERS:
            if i.NAME == user_auth.name:
                return i(user_auth)
        raise LoginErrors.LoginUserAuthNotImplementedError(
                "UserAuth not implemented in LoginAuth: %s" % (
                    user_auth.name
                )
            )

    @abstractmethod
    def authenticate(self, login, password):
        pass

    def __repr__(self):
        return "<LoginAuth class='%s'><UserAuth>%s</UserAuth></LoginAuth>" % (self.__class__, (getattr(self,'_user_auth') or 'Not available'))


class WebLabDBLoginAuth(LoginAuth):
    NAME = UserAuth.WebLabDbUserAuth.NAME

    def __init__(self, user_auth):
        self._user_auth = user_auth

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
        retrieved_password = self._user_auth.hashed_password

        REGEX = "([a-zA-Z0-9]*){([a-zA-Z0-9_-]+)}([a-fA-F0-9]+)"
        mo = re.match(REGEX, retrieved_password)
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

LoginAuth.HANDLERS += (WebLabDBLoginAuth,)



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

class LdapLoginAuth(LoginAuth):

    NAME = UserAuth.LdapUserAuth.NAME

    def __init__(self, user_auth):
        self._user_auth = user_auth

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
                self._user_auth.ldap_uri
            )
        except Exception as e:
            raise LoginErrors.LdapInitializingError(
                "Exception initializing the LDAP module: %s" % e
            )

        dn = "%s@%s" % (login, self._user_auth.domain)
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

LoginAuth.HANDLERS += (LdapLoginAuth,)


class TrustedIpAddressesLoginAuth(LoginAuth):
    NAME = UserAuth.TrustedIpAddressesUserAuth.NAME

    def __init__(self, user_auth):
        self._user_auth = user_auth

    def authenticate(self, login, password):
        if not isinstance(password, ClientAddress.ClientAddress):
            return False
        client_address = password.client_address
        return client_address in self._user_auth.addresses

LoginAuth.HANDLERS += (TrustedIpAddressesLoginAuth,)

class FacebookLoginAuth(LoginAuth):
    NAME = UserAuth.FacebookUserAuth.NAME

    def __init__(self, user_auth):
        self._user_auth = user_auth

    def authenticate(self, login, password):
        return False

LoginAuth.HANDLERS += (FacebookLoginAuth,)

class OpenIDLoginAuth(LoginAuth):
    NAME = UserAuth.OpenIDUserAuth.NAME

    def __init__(self, user_auth):
        self._user_auth = user_auth

    def authenticate(self, login, password):
        return False

LoginAuth.HANDLERS += (OpenIDLoginAuth,)
