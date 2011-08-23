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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import voodoo.gen.coordinator.Address as cAddress
import voodoo.gen.generators.ClientSkel as ClientSkel
import voodoo.gen.protocols.protocols as Protocols

import voodoo.gen.protocols.UnixSocket.Exceptions as Exceptions

import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions

from voodoo.override import Override 

class Address(cAddress.Address):
    
    def __init__(self, machine_id, path_id):
        cAddress.Address.__init__(self)
        if not isinstance(machine_id,basestring):
            raise Exceptions.InvalidArgumentAddressException(
                    "machine_id not a str: %s" % machine_id
                )
        elif not isinstance(path_id,basestring):
            raise Exceptions.InvalidArgumentAddressException(
                    "path_id not a str: %s" % path_id
                )
        self._machine_id = machine_id
        self._path_id = path_id
        self._address = path_id + '@' + machine_id

    @property
    def machine_id(self):
        return self._machine_id

    @property
    def path_id(self):
        return self._path_id

    @Override(cAddress.Address)
    def __cmp__(self, other):
        if not isinstance(other, Address):
            return 1
        cmp_machine_id = cmp(self.machine_id,other.machine_id)
        if cmp_machine_id != 0:
            return cmp_machine_id
        cmp_path_id = cmp(self.path_id,other.path_id)
        if cmp_path_id != 0:
            return cmp_path_id      
        return 0

    @Override(cAddress.Address)
    def __eq__(self, other):
        return self.__cmp__(other) == 0

    @Override(cAddress.Address)
    def _get_address(self):
        return self._address

    @Override(cAddress.Address)
    def create_client(self, methods):
        try:
            client_class = ClientSkel.factory(Protocols.UnixSocket,methods)
        except Exception as e:
            raise ProtocolExceptions.ClientClassCreationException(("Client class creation exception: %s" % e),  e)
        try:
            return client_class(path=self._path_id)
        except Exception as e:
            raise ProtocolExceptions.ClientInstanciationException(("Exception instaciating the client: %s" % e), e)
    
    @Override(cAddress.Address)
    def get_protocol(self):
        return Protocols.UnixSocket
