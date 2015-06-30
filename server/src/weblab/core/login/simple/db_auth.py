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

import re
import hashlib

from weblab.core.login.simple import SimpleAuthnUserAuth

from weblab.core.exc import DbHashAlgorithmNotFoundError, DbInvalidPasswordFormatError

###########################################################################
# 
#    Database based (storing hashed password in the database).
# 


class WebLabDbUserAuth(SimpleAuthnUserAuth):

    NAME = 'DB'

    def __init__(self, auth_configuration, user_auth_configuration):
        self.hashed_password = user_auth_configuration

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
            raise DbInvalidPasswordFormatError( "Invalid password format" )
        first_chars, algorithm, hashed_passwd = mo.groups()

        if algorithm == 'sha':
            algorithm = 'sha1' #TODO

        try:
            hashobj = hashlib.new(algorithm)
        except Exception:
            raise DbHashAlgorithmNotFoundError( "Algorithm %s not found" % algorithm )

        hashobj.update((first_chars + password).encode())
        return hashobj.hexdigest() == hashed_passwd

    def __str__(self):
        return "WebLabDbUserAuth(hashed_password=%r)" % self.hashed_password

    def __repr__(self):
        return "WebLabDbUserAuth(configuration=%r)" % self.hashed_password


