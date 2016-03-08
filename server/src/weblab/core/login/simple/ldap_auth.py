#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 onwards University of Deusto
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
from __future__ import print_function, unicode_literals

import sys
import re
try:
    import ldap
except ImportError:
    LDAP_AVAILABLE = False
else:
    LDAP_AVAILABLE = True

from weblab.core.exc import DbInvalidUserAuthConfigurationError
import voodoo.log as log
import weblab.core.login.exc as LoginErrors

from weblab.core.login.simple import SimpleAuthnUserAuth

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
            raise DbInvalidUserAuthConfigurationError(
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
            print(msg, file=sys.stderr)
            log.log(self, log.level.Error, msg)
            return False

        if not password:
            # The Python LDAP module does not provide any error if the password is empty
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

    def __str__(self):
        return "LdapUserAuth(domain=%r, ldap_uri=%r, base=%r)" % (self.domain, self.ldap_uri, self.base)

    def __repr__(self):
        return "LdapUserAuth(configuration=%r)" % (self.auth_configuration)


