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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import weblab.exc as wlExc

class TranslatorException(wlExc.WebLabException):
    def __init__(self, *args, **kargs):
        wlExc.WebLabException.__init__(self, *args, **kargs)

#
# from TranslatorException
#        

class NotASessionTypeException(TranslatorException):
    def __init__(self, *args, **kargs):
        TranslatorException.__init__(self, *args, **kargs)

class InvalidTranslatorSessionIdException(TranslatorException):
    def __init__(self, *args, **kargs):
        TranslatorException.__init__(self, *args, **kargs)
