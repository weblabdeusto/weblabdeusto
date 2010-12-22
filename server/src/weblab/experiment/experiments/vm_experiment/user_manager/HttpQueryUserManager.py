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
        times_tried = 0 # TODO: Tidy this up
        while(times_tried < 3):
            try:
                response = urllib2.urlopen("%s/?sessionid=%s" % (self._url, sid))
                print response.read()
                break
            except urllib2.HTTPError, ex:
                times_tried += 1
            except urllib2.URLError, ex:
                # These are timeout errors which occur when the virtual OS takes too long to start, which is
                # actually quite common.
                # The above error has the following tuple as its args: (error(10060, 'Operation timed out'),)
                times_tried += 1



