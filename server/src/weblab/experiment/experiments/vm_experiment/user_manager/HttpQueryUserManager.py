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
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

from UserManager import UserManager
import urllib2


HTTP_QUERY_USER_MANAGER_URL = "http_query_user_manager_url"

DEFAULT_HTTP_QUERY_USER_MANAGER_URL = "http://localhost/"


class HttpQueryUserManager(UserManager):
    
    def __init__(self, cfg_manager):
        UserManager.__init__(self, cfg_manager)
        self._url = cfg_manager.get_value(HTTP_QUERY_USER_MANAGER_URL, DEFAULT_HTTP_QUERY_USER_MANAGER_URL) 

    def configure(self, sid):
        response = urllib2.urlopen("%s?sessionid=%s" % (self._url, sid))
        print response.read()