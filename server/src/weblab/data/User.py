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
import weblab.data.UserType as UserType
import weblab.exceptions.data.DataExceptions as DataExceptions

class User(object):
    def __init__(self, login, full_name, email, user_type):
        super(User,self).__init__()
        self.login = login
        self.full_name = full_name
        self.email = email
        self.user_type = user_type

    def __repr__(self):
        return "User(login = '%s', full_name = '%s', email = '%s', user_type = '%s')" % (
                self.login,
                self.full_name,
                self.email,
                self.user_type
            )

class AdminUser(User):
    def __init__(self, login, full_name, email):
        super(AdminUser,self).__init__(
                login     = login,
                full_name = full_name,
                email     = email,
                user_type = UserType.administrator
            )

class ProfessorUser(User):
    def __init__(self, login, full_name, email):
        super(ProfessorUser,self).__init__(
                login     = login,
                full_name = full_name,
                email     = email,
                user_type = UserType.professor
            )

class StudentUser(User):
    def __init__(self, login, full_name, email):
        super(StudentUser,self).__init__(
                login     = login,
                full_name = full_name,
                email     = email,
                user_type = UserType.student
            )

    
def create_user(login,full_name,email,user_type):
    if user_type == UserType.administrator:
        return AdminUser(login,full_name,email)
    elif user_type == UserType.professor:
        return AdminUser(login,full_name,email)
    elif user_type == UserType.student:
        return StudentUser(login,full_name,email)
    else:
        raise DataExceptions.UserTypeNotFound(
                "User type %s not found or supported" % user_type
            )

