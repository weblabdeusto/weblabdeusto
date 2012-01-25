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
import voodoo.gen.exceptions.coordinator.CoordinatorExceptions as CoordExceptions 

class CoordMappingException(CoordExceptions.CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordExceptions.CoordinatorException.__init__(self,*args,**kargs)

class CoordLoadingException(CoordMappingException):
    def __init__(self,message,nested_exception,*args,**kargs):
        CoordMappingException.__init__(
                self, message, nested_exception, *args, **kargs
            )
        self.message = message
        self.nested_exception = nested_exception

class CoordDumpingException(CoordMappingException):
    def __init__(self,message,nested_exception,*args,**kargs):
        CoordMappingException.__init__(
                self, message, nested_exception, *args, **kargs
            )
        self.message = message
        self.nested_exception = nested_exception

class CoordSerializingException(CoordMappingException):
    def __init__(self,message,nested_exception,*args,**kargs):
        CoordMappingException.__init__(
                self, message, nested_exception, *args, **kargs
            )
        self.message = message
        self.nested_exception = nested_exception

