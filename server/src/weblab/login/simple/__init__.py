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

from abc import ABCMeta, abstractmethod

import weblab.db.exc as DbErrors

class UserAuth(object):

    __metaclass__ = ABCMeta

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

##################################################
# 
#      UserAuth Factory: these imports must 
#      be after the UserAuth, since they will
#      refer to this module.
# 

from weblab.login.simple.db_auth import WebLabDbUserAuth
from weblab.login.simple.ldap_auth import LdapUserAuth
from weblab.login.simple.ip_auth import TrustedIpAddressesUserAuth

from weblab.login.web import EXTERNAL_MANAGERS


def create_user_auth(name, auth_configuration, user_auth_configuration):
    if name == WebLabDbUserAuth.NAME:
        return WebLabDbUserAuth(auth_configuration, user_auth_configuration)

    elif name == LdapUserAuth.NAME:
        return LdapUserAuth(auth_configuration, user_auth_configuration)

    elif name == TrustedIpAddressesUserAuth.NAME:
        return TrustedIpAddressesUserAuth(auth_configuration, user_auth_configuration)

    # Any of the Web Protocol Auths (Facebook, OpenID...) are not relevant here.
    elif name in EXTERNAL_MANAGERS.keys():
        return WebProtocolUserAuth()
        
    raise DbErrors.DbUnsupportedUserAuth("UserAuth %s not supported" % name)

