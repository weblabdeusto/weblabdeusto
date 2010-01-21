#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

class User:
    
    def __init__(self, login, name, surname, email, exists, has_auth):
        self.login     = login
        self.full_name = "%s %s" % (name,surname)
        self.email     = email
        self.exists    = exists
        self.has_auth  = has_auth