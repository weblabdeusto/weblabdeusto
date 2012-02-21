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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import weblab.exc as wlExc

class ProxyException(wlExc.WebLabException):
    def __init__(self, *args, **kargs):
        wlExc.WebLabException.__init__(self, *args, **kargs)

#
# from ProxyException
#

class NotASessionTypeException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)

class InvalidReservationIdException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)

class AccessDisabledException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)

class InvalidDefaultTranslatorNameException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)

class FailedToSendCommandException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)

class FailedToSendFileException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)

class NoCurrentReservationException(ProxyException):
    def __init__(self, *args, **kargs):
        ProxyException.__init__(self, *args, **kargs)
