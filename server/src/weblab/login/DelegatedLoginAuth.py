#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

# 
# The systems presented in this file are those which delegate to
# other system the authentication, so no password is sent to LoginServer
# but external tokens. This can be the case of Facebook or SecondLife
# 

import base64
import urllib2

try:
    import json as json_module # Python >= 2.6
    json = json_module
except ImportError:
    import simplejson as json_mod
    json = json_mod

import voodoo.log as log
from voodoo.log import logged
import voodoo.LogLevel as LogLevel
from weblab.data.dto.User import User
from weblab.data.dto.Role import StudentRole

FACEBOOK_TOKEN_VALIDATOR = "https://graph.facebook.com/me?access_token=%s"

# TODO: this could be refactored to be more extensible for other OAuth systems
class Facebook(object):
    def __init__(self, db_manager):
        self._db_manager = db_manager

    @logged(LogLevel.Warning)
    def get_user(self, credentials):
        payload = credentials[credentials.find('.') + 1:]
        payload = payload.replace('-','+').replace('_','/')
        payload = payload + "=="
        try:
            json_content = base64.decodestring(payload)
            data = json.loads(json_content)
            oauth_token = data['oauth_token']
            req = urllib2.urlopen(FACEBOOK_TOKEN_VALIDATOR % oauth_token)
            encoding = req.headers['content-type'].split('charset=')[-1]
            ucontent = unicode(req.read(),encoding)
            user_data = json.loads(ucontent)
            if not user_data['verified']:
                raise Exception("Not verified user!!!")
            login = '%s@facebook' % user_data['id']
            full_name = user_data['name']
            email = user_data.get('email','<not provided>')
            user = User(login, full_name, email, StudentRole())
            return user
        except Exception, e:
            log.log( Facebook, log.LogLevel.Warning, "Error: %s" % e )
            log.log_exc( Facebook, log.LogLevel.Info )
            return ""

    def get_user_id(self, credentials):
        login = self.get_user(credentials).login
        # login is "13122142321@facebook"
        return login.split('@')[0]

