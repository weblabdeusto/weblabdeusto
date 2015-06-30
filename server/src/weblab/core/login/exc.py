#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
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
from __future__ import print_function, unicode_literals
import weblab.exc as wlExc

#
# from WebLabError
#

class LoginError(wlExc.WebLabError):
    def __init__(self,*args,**kargs):
        wlExc.WebLabError.__init__(self,*args,**kargs)

#
# from LoginError
#

class InvalidCredentialsError(LoginError):
    def __init__(self,*args,**kargs):
        LoginError.__init__(self,*args,**kargs)

class UnableToCompleteOperationError(LoginError):
    def __init__(self,*args,**kargs):
        LoginError.__init__(self,*args,**kargs)

class LoginAuthError(LoginError):
    def __init__(self,*args,**kargs):
        LoginError.__init__(self,*args,**kargs)

class LdapAuthError(LoginError):
    def __init__(self,*args,**kargs):
        LoginError.__init__(self,*args,**kargs)

#
# from LoginAuthError
#

class LoginUserAuthNotImplementedError(LoginAuthError):
    def __init__(self,*args,**kargs):
        LoginAuthError.__init__(self,*args,**kargs)

#
# from LdapAuthError
#

class LdapInitializingError(LdapAuthError):
    def __init__(self,*args,**kargs):
        LdapAuthError.__init__(self,*args,**kargs)

class LdapBindingError(LdapAuthError):
    def __init__(self,*args,**kargs):
        LdapAuthError.__init__(self,*args,**kargs)
