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
import voodoo.gen.coordinator.Access as Access

name = "SOAP"

class SOAPNetwork(Access.IpBasedNetwork):
    
    def __init__(self,address):
        Access.IpBasedNetwork.__init__(self,address)
        
    def get_protocol(self):
        import voodoo.gen.protocols.SOAP.Network as Network
        return Network
