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
class PermissionType(object):
    def __init__(self, id, name, description):
        super(PermissionType,self).__init__()
        self.id          = id
        self.name        = name
        self.description = description

class PermissionParameterType(object):
    def __init__(self, id, name, type, description, permission):
        super(PermissionParameterType,self).__init__()
        self.id          = id
        self.name        = name
        self.type        = type
        self.description = description
        self.permission  = permission

class PermissionParameter(object):
    def __init__(self, id, permission_parameter_type, value):
        super(PermissionParameter,self).__init__()
        self.id             = id
        self.parameter_type = permission_parameter_type
        self.value          = value

class PermissionInstance(object):
    def __init__(self, id, permission_type, date, name, comments, parameters = None):
        super(PermissionInstance,self).__init__()
        self.id                     = id
        self.permission_type        = permission_type
        self.date                   = date
        self.name                   = name
        self.comments               = comments
        if parameters == None:
            self.parameters     = {}
        else:
            self.parameters     = parameters

class UserPermissionType(PermissionType):
    def __init__(self,*args,**kargs):
        super(UserPermissionType,self).__init__(*args,**kargs)

class UserPermissionParameterType(PermissionParameterType):
    def __init__(self,*args,**kargs):
        super(UserPermissionParameterType,self).__init__(*args,**kargs)

class UserPermissionParameter(PermissionParameter):
    def __init__(self,*args,**kargs):
        super(UserPermissionParameter,self).__init__(*args,**kargs)

class UserPermissionInstance(PermissionInstance):
    def __init__(self,*args,**kargs):
        super(UserPermissionInstance,self).__init__(*args,**kargs)

class GroupPermissionType(PermissionType):
    def __init__(self,*args,**kargs):
        super(GroupPermissionType,self).__init__(*args,**kargs)

class GroupPermissionParameterType(PermissionParameterType):
    def __init__(self,*args,**kargs):
        super(GroupPermissionParameterType,self).__init__(*args,**kargs)

class GroupPermissionParameter(PermissionParameter):
    def __init__(self,*args,**kargs):
        super(GroupPermissionParameter,self).__init__(*args,**kargs)

class GroupPermissionInstance(PermissionInstance):
    def __init__(self,*args,**kargs):
        super(GroupPermissionInstance,self).__init__(*args,**kargs)
