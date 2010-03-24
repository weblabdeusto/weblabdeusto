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
import weblab.exceptions.WebLabExceptions as WebLabExceptions

class DataException(WebLabExceptions.WebLabException):
    def __init__(self,*args,**kargs):
        WebLabExceptions.WebLabException.__init__(self,*args,**kargs)