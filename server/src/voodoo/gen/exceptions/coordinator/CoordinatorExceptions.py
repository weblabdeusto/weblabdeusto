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

import voodoo.gen.exceptions.exceptions as genExceptions

class CoordinatorException(genExceptions.GeneratorException):
    def __init__(self,*args,**kargs):
        genExceptions.GeneratorException.__init__(self,*args,**kargs)

class CoordInvalidAddressName(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

class CoordInvalidServer(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

class CoordInvalidAddressParams(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

class CoordInvalidLevelAddress(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

class CoordInvalidKey(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

class CoordNodeNotFound(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

class CoordMapNotInitialized(CoordinatorException):
    def __init__(self,*args,**kargs):
        CoordinatorException.__init__(self,*args,**kargs)

# CoordNodeNotFound children

class CoordMachineNotFound(CoordNodeNotFound):
    def __init__(self,*args,**kargs):
        CoordNodeNotFound.__init__(self,*args,**kargs)

class CoordInstanceNotFound(CoordNodeNotFound):
    def __init__(self,*args,**kargs):
        CoordNodeNotFound.__init__(self,*args,**kargs)

class CoordServerNotFound(CoordNodeNotFound):
    def __init__(self,*args,**kargs):
        CoordNodeNotFound.__init__(self,*args,**kargs)

