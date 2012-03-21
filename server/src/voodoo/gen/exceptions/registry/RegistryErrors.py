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

class RegistryError(genErrors.GeneratorError):
    def __init__(self,*args,**kargs):
        genErrors.GeneratorError.__init__(self,*args,**kargs)

class AddressAlreadyRegisteredError(RegistryError):
    def __init__(self,*args,**kargs):
        RegistryError.__init__(self,*args,**kargs)

class ServerNotFoundInRegistryError(RegistryError):
    def __init__(self,*args,**kargs):
        RegistryError.__init__(self,*args,**kargs)

