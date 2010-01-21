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

class CoordVersionException(genExceptions.GeneratorException):
    def __init__(self,*args,**kargs):
        genExceptions.GeneratorException.__init__(self,*args,**kargs)

class CoordVersionNotAnActionException(CoordVersionException):
    def __init__(self,*args,**kargs):
        CoordVersionException.__init__(self,*args,**kargs)

class CoordVersionNotAnAddressException(CoordVersionException):
    def __init__(self,*args,**kargs):
        CoordVersionException.__init__(self,*args,**kargs)
