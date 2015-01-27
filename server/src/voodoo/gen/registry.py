#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 onwards University of Deusto
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
from .exc import AddressAlreadyRegisteredError, ServerNotFoundInRegistryError

class ServerRegistry(object):
    """
        Inside each application, there is a ServerRegistry, which indexes
        all the servers with Direct Connection available in the server.
        This way, if a Coordination Server says that "there is a DatabaseServer
        at this address", and the Server is in the same application, the server
        will be able to be found in this registry.
    """
    def __init__(self):
        self._servers = {}

    def register(self, address, server, force = False):
        if not force and address in self._servers:
            raise AddressAlreadyRegisteredError('Key %s already found in ServerRegistry' % address)
        self._servers[address] = server

    def deregister(self, address):
        if not self._servers.has_key(address):
            raise ServerNotFoundInRegistryError(
                'Address %s not found in registry' % address
            )

        self._servers.pop(address)

    def __setitem__(self, address, server):
        self.register(address, server)
        return server

    def __getitem__(self, address):
        return self._servers[address]

    def clear(self):
        self._servers.clear()

GLOBAL_REGISTRY = ServerRegistry()

