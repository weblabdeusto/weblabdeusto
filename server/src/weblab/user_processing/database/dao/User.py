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
import weblab.exceptions.database.DatabaseExceptions as DbExceptions
import weblab.data.User as BsUser

class User(object):
    admin     = 'administrator'
    professor = 'professor'
    student   = 'student'
    def __init__(self, id, login, full_name, email, user_type):
        super(User,self).__init__()
        self.id        = id
        self.login     = login
        self.full_name = full_name
        self.email     = email
        self.user_type = user_type
    def __repr__(self):
        return "User %s; id = %s, login = %s, full_name = %s, email = %s " % (
                self.__class__,
                self.id,
                self.login,
                self.full_name,
                self.email,
            )
    def to_business(self):
        raise NotImplementedError("%s does not implement to_business" % self)

class AdminUser(User):
    def __init__(self, id, login, full_name, email):
        super(AdminUser,self).__init__(
                id        = id,
                login     = login,
                full_name = full_name,
                email     = email,
                user_type = User.admin
            )
    def to_business(self):
        return BsUser.AdminUser(
                self.login,
                self.full_name,
                self.email
            )

class ProfessorUser(User):
    def __init__(self, id, login, full_name, email):
        super(ProfessorUser,self).__init__(
                id        = id,
                login     = login,
                full_name = full_name,
                email     = email,
                user_type = User.professor
            )

    def to_business(self):
        return BsUser.ProfessorUser(
                self.login,
                self.full_name,
                self.email
            )


class StudentUser(User):
    def __init__(self, id, login, full_name, email):
        super(StudentUser,self).__init__(
                id        = id,
                login     = login,
                full_name = full_name,
                email     = email,
                user_type = User.student
            )

    def to_business(self):
        return BsUser.StudentUser(
                self.login,
                self.full_name,
                self.email
            )

    
def create_user(id,login,full_name,email,user_type):
    if user_type == User.admin:
        return AdminUser(id,login,full_name,email)
    elif user_type == User.professor:
        return ProfessorUser(id,login,full_name,email)
    elif user_type == User.student:
        return StudentUser(id,login,full_name,email)
    else:
        raise DbExceptions.DaoUserNotFoundException("Can't find user_type <%s>" % user_type)

