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
import weblab.experiment.exc as ExperimentExceptions

class UdPicExperimentException(ExperimentExceptions.ExperimentException):
    def __init__(self,*args,**kargs):
        ExperimentExceptions.ExperimentException.__init__(self,*args,**kargs)

class UdPicBoardCommandException(UdPicExperimentException):
    def __init__(self, *args, **kargs):
        UdPicExperimentException.__init__(self, *args, **kargs)

class InvalidUdPicBoardCommandException(UdPicBoardCommandException):
    def __init__(self, *args, **kargs):
        UdPicBoardCommandException.__init__(self, *args, **kargs)

class IllegalStatusUdPicBoardCommandException(UdPicBoardCommandException):
    def __init__(self, *args, **kargs):
        UdPicBoardCommandException.__init__(self, *args, **kargs)

class UdPicInvalidResponseException(UdPicExperimentException):
    def __init__(self, *args, **kargs):
        ExperimentExceptions.ExperimentException.__init__(self, *args, **kargs)

