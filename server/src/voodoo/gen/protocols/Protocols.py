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

SOAP           = 'SOAP'
Direct         = 'Direct'
InternetSocket = 'InternetSocket'
UnixSocket     = 'UnixSocket'
XMLRPC         = 'XMLRPC'

def getProtocolValues():
    return SOAP, Direct, InternetSocket, UnixSocket, XMLRPC

def isProtocols(protocol):
    return protocol in getProtocolValues()
