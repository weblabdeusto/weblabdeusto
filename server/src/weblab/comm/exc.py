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
import weblab.exc as wlExc

class FacadeException(wlExc.WebLabException):
    def __init__(self,*args,**kargs):
        wlExc.WebLabException.__init__(self,*args,**kargs)

class MisconfiguredException(FacadeException):
    def __init__(self, msg, *args, **kargs):
        FacadeException.__init__(self, msg, *args, **kargs)
        self.message = msg

