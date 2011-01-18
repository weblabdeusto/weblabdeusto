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

FACEBOOK_TOKEN_VALIDATOR = "https://graph.facebook.com/me?access_token=%s"

# TODO: this could be refactored to be more extensible for other OAuth systems
class Facebook(object):
    def __init__(self, db_manager):
        self._db_manager = db_manager
    
    def get_user_id(self, credentials):
        payload = credentials[credentials.find('.') + 1:]
        payload = payload.replace('-','+').replace('_','/')
        payload = payload + "=="
        try:
            json_content = base64.decodestring(payload)
            data = json.loads(json_content)
            oauth_token = data['oauth_token']
            user_data = json.load(urllib2.urlopen(FACEBOOK_TOKEN_VALIDATOR % oauth_token))
            facebook_id = user_data['id']
            return facebook_id
        except Exception, e:
            log.log( Facebook, log.LogLevel.Warning, "Error: %s" % e )
            log.log_exc( Facebook, log.LogLevel.Info )
            return ""

