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
import weblab.exc as wlExc

#
# from WebLabException
#

class LoginException(wlExc.WebLabException):
    def __init__(self,*args,**kargs):
        wlExc.WebLabException.__init__(self,*args,**kargs)

#
# from LoginException
#

class InvalidCredentialsException(LoginException):
    def __init__(self,*args,**kargs):
        LoginException.__init__(self,*args,**kargs)

class UnableToCompleteOperationException(LoginException):
    def __init__(self,*args,**kargs):
        LoginException.__init__(self,*args,**kargs)

class LoginAuthException(LoginException):
    def __init__(self,*args,**kargs):
        LoginException.__init__(self,*args,**kargs)

class LdapAuthException(LoginException):
    def __init__(self,*args,**kargs):
        LoginException.__init__(self,*args,**kargs)

#
# from LoginAuthException
#

class LoginUserAuthNotImplementedException(LoginAuthException):
    def __init__(self,*args,**kargs):
        LoginAuthException.__init__(self,*args,**kargs)

#
# from LdapAuthException
#

class LdapInitializingException(LdapAuthException):
    def __init__(self,*args,**kargs):
        LdapAuthException.__init__(self,*args,**kargs)

class LdapBindingException(LdapAuthException):
    def __init__(self,*args,**kargs):
        LdapAuthException.__init__(self,*args,**kargs)  
