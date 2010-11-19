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
import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions

class UdXilinxExperimentException(ExperimentExceptions.ExperimentException):
    def __init__(self,*args,**kargs):
        ExperimentExceptions.ExperimentException.__init__(self,*args,**kargs)

class UdBoardCommandException(UdXilinxExperimentException):
    def __init__(self, *args, **kargs):
        UdXilinxExperimentException.__init__(self, *args, **kargs)

class InvalidUdBoardCommandException(UdBoardCommandException):
    def __init__(self, *args, **kargs):
        UdBoardCommandException.__init__(self, *args, **kargs)

class IllegalStatusUdBoardCommandException(UdBoardCommandException):
    def __init__(self, *args, **kargs):
        UdBoardCommandException.__init__(self, *args, **kargs)

class InvalidDeviceToProgramException(UdBoardCommandException):
    def __init__(self, *args, **kargs):
        UdBoardCommandException.__init__(self, *args, **kargs)

class InvalidDeviceToSendCommandsException(UdBoardCommandException):
    def __init__(self, *args, **kargs):
        UdBoardCommandException.__init__(self, *args, **kargs)

class InvalidXilinxDeviceException(UdBoardCommandException):
    def __init__(self, *args, **kargs):
        UdBoardCommandException.__init__(self, *args, **kargs)