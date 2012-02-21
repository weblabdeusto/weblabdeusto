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

import voodoo.gen.exceptions.exceptions as genExceptions

class AccessException(genExceptions.GeneratorException):
    def __init__(self,*args,**kargs):
        genExceptions.GeneratorException.__init__(self,*args,**kargs)

class AccessNotAnAddressException(AccessException):
    def __init__(self,*args,**kargs):
        AccessException.__init__(self,*args,**kargs)

class AccessNotAnIpAddressException(AccessNotAnAddressException):
    def __init__(self,*args,**kargs):
        AccessNotAnAddressException.__init__(self,*args,**kargs)

class AccessInvalidIpBasedFormat(AccessException):
    def __init__(self,*args,**kargs):
        AccessException.__init__(self,*args,**kargs)

class AccessInvalidPort(AccessInvalidIpBasedFormat):
    def __init__(self,*args,**kargs):
        AccessInvalidIpBasedFormat.__init__(self,*args,**kargs)

