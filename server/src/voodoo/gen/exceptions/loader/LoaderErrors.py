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

import voodoo.gen.exceptions.exceptions as exceptions

class LoaderError(exceptions.GeneratorError):
    def __init__(self, *args, **kargs):
        exceptions.GeneratorError.__init__(self,*args,**kargs)

class InvalidConfigurationError(LoaderError):
    def __init__(self,*args,**kargs):
        LoaderError.__init__(self,*args,**kargs)

class InvalidSyntaxFileConfigurationError(InvalidConfigurationError):
    def __init__(self,what,file,*args,**kargs):
        InvalidConfigurationError.__init__(self,what,file,*args,**kargs)
        self.file = file

