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

from experiments.vm.user_manager.manager import UserManager

class DummyUserManager(UserManager):
    
    def __init__(self, cfg_manager):
        UserManager.__init__(self, cfg_manager)

    def configure(self, sid):
        print "Configuring with sid %s" % (sid)
        
