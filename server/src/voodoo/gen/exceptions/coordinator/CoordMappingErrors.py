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
import voodoo.gen.exceptions.coordinator.CoordinatorErrors as CoordErrors

class CoordMappingError(CoordErrors.CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordErrors.CoordinatorError.__init__(self,*args,**kargs)

class CoordLoadingError(CoordMappingError):
    def __init__(self,message,nested_exception,*args,**kargs):
        CoordMappingError.__init__(
                self, message, nested_exception, *args, **kargs
            )
        self.message = message
        self.nested_exception = nested_exception

class CoordDumpingError(CoordMappingError):
    def __init__(self,message,nested_exception,*args,**kargs):
        CoordMappingError.__init__(
                self, message, nested_exception, *args, **kargs
            )
        self.message = message
        self.nested_exception = nested_exception

class CoordSerializingError(CoordMappingError):
    def __init__(self,message,nested_exception,*args,**kargs):
        CoordMappingError.__init__(
                self, message, nested_exception, *args, **kargs
            )
        self.message = message
        self.nested_exception = nested_exception

