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

class UdXilinxExperimentError(ExperimentErrors.ExperimentError):
    def __init__(self,*args,**kargs):
        ExperimentErrors.ExperimentError.__init__(self,*args,**kargs)

class UdBoardCommandError(UdXilinxExperimentError):
    def __init__(self, *args, **kargs):
        UdXilinxExperimentError.__init__(self, *args, **kargs)

class InvalidUdBoardCommandError(UdBoardCommandError):
    def __init__(self, *args, **kargs):
        UdBoardCommandError.__init__(self, *args, **kargs)

class IllegalStatusUdBoardCommandError(UdBoardCommandError):
    def __init__(self, *args, **kargs):
        UdBoardCommandError.__init__(self, *args, **kargs)

class InvalidDeviceToProgramError(UdBoardCommandError):
    def __init__(self, *args, **kargs):
        UdBoardCommandError.__init__(self, *args, **kargs)

class InvalidDeviceToSendCommandsError(UdBoardCommandError):
    def __init__(self, *args, **kargs):
        UdBoardCommandError.__init__(self, *args, **kargs)

class InvalidXilinxDeviceError(UdBoardCommandError):
    def __init__(self, *args, **kargs):
        UdBoardCommandError.__init__(self, *args, **kargs)