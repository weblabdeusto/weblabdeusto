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
import voodoo.gen.coordinator.CoordAddress as CoordAddress

import voodoo.gen.protocols.Protocols as Protocols

import voodoo.gen.generators.ClientSkel as ClientSkel

import voodoo.gen.protocols.Direct.ServerDirect as ServerDirect

import voodoo.gen.registry.ServerRegistry as ServerRegistry

import voodoo.gen.exceptions.registry.RegistryExceptions as RegistryExceptions
import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

from voodoo.override import Override

import voodoo.gen.protocols.Direct.Exceptions as Exceptions

class Address(cAddress.Address):
    
    def __init__(self, machine_id, instance_id, server_id):
        cAddress.Address.__init__(self)
        if not isinstance(machine_id,basestring):
            raise Exceptions.InvalidArgumentAddressException(
                    "machine_id not a str: %s" % server_id
                )
        elif not isinstance(instance_id,basestring):
            raise Exceptions.InvalidArgumentAddressException(
                    "instance_id not a str: %s" % server_id
                )
        elif not isinstance(server_id,basestring):
            raise Exceptions.InvalidArgumentAddressException(
                    "server_id not a str: %s" % server_id
                )
        self._machine_id = machine_id
        self._instance_id = instance_id
        self._server_id = server_id
        self._address = server_id + ':' + instance_id + '@' + machine_id

    def __repr__(self):
        return "<Direct.Address %s>" % self._address

    @property
    def machine_id(self):
        return self._machine_id

    @property
    def instance_id(self):
        return self._instance_id

    @property
    def server_id(self):
        return self._server_id

    @Override(cAddress.Address)
    def __cmp__(self,other):
        if not isinstance(other,Address):
            return 1
        cmp_machine_id = cmp(self.machine_id,other.machine_id)
        if cmp_machine_id != 0:
            return cmp_machine_id
        cmp_instance_id = cmp(self.instance_id,other.instance_id)
        if cmp_instance_id != 0:
            return cmp_instance_id
        cmp_server_id = cmp(self.server_id,other.server_id)
        if cmp_server_id != 0:
            return cmp_server_id        
        return 0

    @Override(cAddress.Address)
    def __eq__(self, other):
        return self.__cmp__(other) == 0

    @Override(cAddress.Address)
    def _get_address(self):
        return self._address

    @Override(cAddress.Address)
    def create_client(self,methods):
        registry = ServerRegistry.get_instance()
        try:
            server = registry.get_server(
                ServerDirect._SERVER_PREFIX +self._server_id
            )
        except RegistryExceptions.RegistryException as rex:
            raise ProtocolExceptions.ClientCreationException(
                    ("Registry exception while retrieving server from registry: %s" % rex),
                    rex
            )
        try:
            client_class = ClientSkel.factory(Protocols.Direct,methods)
        except Exception as e:
            raise ProtocolExceptions.ClientClassCreationException(
                    ("Client class creation exception: %s" % e),
                    e
                )
        try:
            return client_class(server)
        except Exception as e:
            raise ProtocolExceptions.ClientInstanciationException(
                    ("Exception instaciating the client: %s" % e),
                    e
                )
    
    @Override(cAddress.Address)
    def get_protocol(self):
        return Protocols.Direct
        
def from_coord_address(coord_address):
    if not isinstance(coord_address,CoordAddress.CoordAddress):
        raise Exceptions.NotACoordAddressException(
                "Not a CoordAddress: %s" % coord_address
            )
    return Address(
            coord_address.machine_id,
            coord_address.instance_id,
            coord_address.server_id
        )

