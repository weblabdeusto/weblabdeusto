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
from __future__ import print_function, unicode_literals
import weblab.exc as wlExc

class ExperimentError(wlExc.WebLabError):
    def __init__(self,*args,**kargs):
        wlExc.WebLabError.__init__(self,*args,**kargs)

class FeatureNotImplementedError(ExperimentError):
    def __init__(self, *args, **kargs):
        ExperimentError.__init__(self,*args,**kargs)

class SendingFileFailureError(ExperimentError):
    def __init__(self, *args, **kargs):
        ExperimentError.__init__(self, *args, **kargs)

class SendingCommandFailureError(ExperimentError):
    def __init__(self, *args, **kargs):
        ExperimentError.__init__(self, *args, **kargs)

