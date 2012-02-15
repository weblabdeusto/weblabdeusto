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
import voodoo.lock as lock
from voodoo.lock import locked
import voodoo.gen.exceptions.registry.RegistryExceptions as RegistryExceptions

class ServerRegistry(object):
    """
        Inside each application, there is a ServerRegistry, which indexes
        all the servers with Direct Connection available in the server.
        This way, if a Coordination Server says that "there is a DatabaseServer
        at this address", and the Server is in the same application, the server
        will be able to be found in this registry.
    """
    def __init__(self):
        object.__init__(self)

        self._servers            = {}
        self._servers_lock       = lock.RWLock()
        self._servers_read_lock  = self._servers_lock.read_lock()
        self._servers_write_lock = self._servers_lock.write_lock()

    @locked('_servers_write_lock')
    def register_server(self, address, server):
        if self._servers.has_key(address):
            raise RegistryExceptions.AddressAlreadyRegisteredException('Key %s already found in ServerRegistry' % address)
        self._servers[address] = server

    @locked('_servers_write_lock')
    def reregister_server(self,address,server):
        self._servers[address] = server

    @locked('_servers_write_lock')
    def deregister_server(self, address):
        if not self._servers.has_key(address):
            raise RegistryExceptions.ServerNotFoundInRegistryException(
                'Address %s not found in registry' % address
            )

        self._servers.pop(address)

    @locked('_servers_read_lock')
    def get_server(self, address):
        if not self._servers.has_key(address):
            raise RegistryExceptions.ServerNotFoundInRegistryException(
                'Address %s not found in registry' % address
            )
        return self._servers[address]

    @locked('_servers_write_lock')
    def clear(self):
        self._servers.clear()

_registry = ServerRegistry()

def get_instance():
    return _registry

