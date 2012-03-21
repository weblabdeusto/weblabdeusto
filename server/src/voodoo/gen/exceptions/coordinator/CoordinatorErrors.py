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

import voodoo.gen.exceptions.exceptions as genErrors

class CoordinatorError(genErrors.GeneratorError):
    def __init__(self,*args,**kargs):
        genErrors.GeneratorError.__init__(self,*args,**kargs)

class CoordInvalidAddressName(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

class CoordInvalidServer(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

class CoordInvalidAddressParams(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

class CoordInvalidLevelAddress(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

class CoordInvalidKey(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

class CoordNodeNotFound(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

class CoordMapNotInitialized(CoordinatorError):
    def __init__(self,*args,**kargs):
        CoordinatorError.__init__(self,*args,**kargs)

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

