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

import voodoo.gen.exceptions.exceptions as exceptions

class LoaderException(exceptions.GeneratorException):
    def __init__(self, *args, **kargs):
        exceptions.GeneratorException.__init__(self,*args,**kargs)

class InvalidConfigurationException(LoaderException):
    def __init__(self,*args,**kargs):
        LoaderException.__init__(self,*args,**kargs)

class InvalidSyntaxFileConfigurationException(InvalidConfigurationException):
    def __init__(self,what,file,*args,**kargs):
        InvalidConfigurationException.__init__(self,what,file,*args,**kargs)
        self.file = file

