#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

from abc import ABCMeta, abstractmethod
from weblab.core.wl import weblab_api
assert weblab_api is not None # avoid warnings
from flask import request

def get_argument(name, default = None):
    value = request.args.get(name)
    if value is None: 
        if request.method == 'POST':
            return request.form.get(name, default)
        return default
    return value

class ExternalSystemManager(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user(self, credentials):
        """Create a User instance with the data of this user."""

    @abstractmethod
    def get_user_id(self, credentials):
        """Create a string which is a unique identifier for this user in the foreign system"""

#########################################################
# 
#     Registry of the web plug-ins and User Auths
# 

import login
assert login is not None # avoid warnings

from weblab.core.login.web.facebook   import FacebookManager
from weblab.core.login.web.openid_web import OpenIdManager
from weblab.core.login.web.uned_sso   import UnedSSOManager

EXTERNAL_MANAGERS = {
    FacebookManager.NAME : FacebookManager(),
    OpenIdManager.NAME   : OpenIdManager(),
    UnedSSOManager.NAME  : UnedSSOManager(),
    # Your plug-in here
}
