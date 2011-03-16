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

import weblab.facade.WebFacadeServer as WebFacadeServer

class LoginMethod(WebFacadeServer.Method):
    path = '/login/'

    def run(self):
        return_value = "I have a direct reference to %s" % self.server
        return_value += ", so I can call directly %s" % self.server.login
        return_value += ", for instance: %s" % self.server.login('student1','password')
        return_value += ", you called %s " % self.req.path
        return_value += ", and a configuration manager (%s) " % self.cfg_manager
        return_value += ", btw, your IP is: %s (unknown if not being forwarded by Apache)" % self.get_context().get_ip_address()
        
        return return_value

