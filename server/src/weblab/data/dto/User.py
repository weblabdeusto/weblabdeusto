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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

class User(object):
    
    def __init__(self, login, full_name, email, role):
        super(User,self).__init__()
        self.login = login
        self.full_name = full_name
        self.email = email
        self.role = role

    def __repr__(self):
        return "User(login = '%s', full_name = '%s', email = '%s', role = %r)" % (
                self.login,
                self.full_name,
                self.email,
                self.role
            )

        
class Role(object):
    
    def __init__(self, name):
        super(Role, self).__init__()
        self.name = name
        
    def __repr__(self):
        return "Role(name = '%s')" % (
                self.name
            )    