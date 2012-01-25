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
import voodoo.gen.coordinator.Address as cAddress

import voodoo.gen.protocols.protocols as Protocols

import voodoo.gen.protocols.XMLRPC.ClientXMLRPC as ClientXMLRPC

import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

from voodoo.override import Override

class Address(cAddress.IpBasedAddress):

    FORMAT = "%(address)s:%(port)s%(uri)s@%(net_name)s"
    REGEX_FORMAT = FORMAT % {
        'address'   : '(.+)', #It can be whatever.com, for example
        'net_name'  : '(.+)', #Any name
        'port'      : '([0-9]{1,5})', #Port
        'uri'       : '(/[/_%0-9a-zA-Z]*)?'
    }

    def __init__(self, address):
        cAddress.IpBasedAddress.__init__(self,address)

    def _parse(self, groups):
        ip_addr, port, uri, net_name = groups
        cAddress.IpBasedAddress._parse(self, (ip_addr, port, net_name))
        self._uri = uri or '/'

    @Override(cAddress.IpBasedAddress)
    def create_client(self,methods):
        try:
            client_class = ClientXMLRPC.generate(methods)
        except Exception as e:
            raise ProtocolExceptions.ClientClassCreationException(
                    ("Client class creation exception: %s" % e),
                    e
                )
        try:
            return client_class(url = self.ip_address, port = self.port, uri = self.uri)
        except Exception as e:
            raise ProtocolExceptions.ClientInstanciationException(("Unable to instanciate the XMLRPC client: %s" % e),e)

    def __repr__(self):
        return "<XMLRPCAddress: %s>" % self.address

    @Override(cAddress.IpBasedAddress)
    def get_protocol(self):
        return Protocols.XMLRPC

    @Override(cAddress.IpBasedAddress)
    def __cmp__(self,other):
        return cAddress.IpBasedAddress._compare(self,other)

    @Override(cAddress.IpBasedAddress)
    def __eq__(self, other):
        return self.__cmp__(other) == 0

    @property
    def uri(self):
        return self._uri

