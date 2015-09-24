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
from __future__ import print_function, unicode_literals
from .exc import AddressAlreadyRegisteredError, ServerNotFoundInRegistryError

class ComponentRegistry(dict):
    """
        Inside each process, there is a ServerRegistry, which indexes
        all the components with Direct Connection available in the server.
    """

    def register(self, address, component, force = False):
        if not force and address in self:
            raise AddressAlreadyRegisteredError('Key %s already found in ServerRegistry' % address)
        dict.__setitem__(self, address, component)

    def deregister(self, address):
        if not address in self:
            raise ServerNotFoundInRegistryError(
                'Address %s not found in registry' % address
            )

        self.pop(address)

    def __setitem__(self, address, component):
        self.register(address, component)
        return component

GLOBAL_REGISTRY = ComponentRegistry()

