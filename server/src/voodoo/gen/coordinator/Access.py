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

from abc import ABCMeta, abstractmethod

import voodoo.gen.exceptions.coordinator.AccessErrors as AccessErrors
import voodoo.gen.coordinator.Address as Address

class Access(object):
    """A CoordServer will have different "Access"es. For example, a Server can have an Access for
    "Direct connections" (with protocol = Direct), and an Access for SOAP, and inside this Access,
    it could have different "SOAPNetwork"s. For example, it could have 2 different networks, one
    with address '192.168.0.1:8080@Network1' and another with address '130.206.136.137:8080@Network2'. The
    Direct or machine access would have one network with a CoordAddress address.

    Right now we don't have any MachineNetwork available, since we don't have any IPC protocol available such
    as dbus.
    """
    def __init__(self, protocol, access_level, networks):
        self.protocol  = protocol
        self.access_level = access_level
        self.networks = list(networks)

    def possible_connections(self,other):
        if other.access_level != self.access_level or other.protocol != self.protocol:
            return []
        #Now, let's check networks

        return_value = []
        for i in self.networks:
            for j in i.check(other):
                return_value.append(j)
        return return_value

class Network(object):

    __metaclass__ = ABCMeta

    def __init__(self, address):
        if not isinstance(address,Address.Address):
            raise AccessErrors.AccessNotAnAddressError("Not an Address: %s" % address)
        self.address = address

    @abstractmethod
    def check(self,other):
        """ check(self,other) -> [Network1,...]

        Given this network and an instance of Access called "other",
        check will return a list of networks of "other" which are
        interoperable with this network
        """

    @abstractmethod
    def get_protocol(self):
        """ get_protocol(self) -> protocol_module

        Given this network, it will return the module of the protocol
        (SOAP,Direct, and so on).
        """

class IpBasedNetwork(Network):
    def __init__(self,address):
        """ Address will have this format: 'IP:PORT@NETWORK_NAME' """
        if not isinstance(address,Address.IpBasedAddress):
            raise AccessErrors.AccessNotAnIpAddressError("Not an IpBasedAddress: %s" % address)
        Network.__init__(self,address)
    def check(self,other):
        return [ i for i in other.networks
            if isinstance(i,IpBasedNetwork) and self.address._net_name == i.address._net_name ]

