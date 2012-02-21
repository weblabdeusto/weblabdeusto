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
import weblab.experiment.exc as ExperimentErrors

class UdGpibExperimentError(ExperimentErrors.ExperimentError):
    def __init__(self,*args,**kargs):
        ExperimentErrors.ExperimentError.__init__(self,*args,**kargs)

class UnknownUdGpibCommandError(UdGpibExperimentError):
    def __init__(self,*args,**kargs):
        UdGpibExperimentError.__init__(self,*args,**kargs)
