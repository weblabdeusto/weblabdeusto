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
import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

class XMLRPCInvalidServerParameterException(ProtocolExceptions.InvalidServerParameterException):
    def __init__(self,*args,**kargs):
        ProtocolExceptions.InvalidServerParameterException.__init__(self,*args,**kargs)

class UnknownFaultType(ProtocolExceptions.RemoteException):
    def __init__(self,*args,**kargs):
        ProtocolExceptions.RemoteException(self,*args,**kargs)

