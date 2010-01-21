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
import voodoo.exceptions.exceptions as VoodooExceptions

class ConfigurationException(VoodooExceptions.VoodooException):
    def __init__(self,*args,**kargs):
        VoodooExceptions.VoodooException.__init__(self,*args,**kargs)

class KeyNotFoundException(ConfigurationException):
    def __init__(self, msg, key, *args, **kargs):
        ConfigurationException.__init__(self, msg, key, *args, **kargs)
        self.msg = msg
        self.key = key

class KeysNotFoundException(ConfigurationException):
    def __init__(self, *args, **kargs):
        ConfigurationException.__init__(self, *args, **kargs)

class NotAModuleException(ConfigurationException):
    def __init__(self, *args, **kargs):
        ConfigurationException.__init__(self, *args, **kargs)
