#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

class ParameterConfiguration(object):
    def __init__(self, name, value):
        super(ParameterConfiguration, self).__init__()
        self.name  = name
        self.value = value

class CoordinationConfiguration(object):
    def __init__(self, parameters):
        super(CoordinationConfiguration, self).__init__()
        self.parameters = parameters

class CoordinationsConfiguration(object):
    def __init__(self, coordinations):
        super(CoordinationsConfiguration, self).__init__()
        self.coordinations           = coordinations
        self.filled_level         = None
        self.filled_coordinations = []
    def append_filled_coordination(self, filled_coordination):
        self.filled_coordinations.append(filled_coordination)

class CreationConfiguration(object):
    def __init__(self, parameters):
        super(CreationConfiguration, self).__init__()
        self.parameters = parameters

class ProtocolConfiguration(object):
    def __init__(self, name, coordinations, creation):
        super(ProtocolConfiguration, self).__init__()
        self.name               = name
        self.coordinations      = coordinations
        self.creation           = creation
        self.filled_creation    = None

class ServerConfiguration(object):
    def __init__(self, address, configurations, server_type, server_type_module, methods, implementation, restrictions, protocols):
        super(ServerConfiguration, self).__init__()
        self.address            = address
        self._configurations    = configurations
        self.server_type        = server_type
        self.server_type_module = server_type_module
        self.methods            = methods
        self.implementation     = implementation
        self.restrictions       = restrictions
        self._protocols         = protocols

    @property
    def protocols(self):
        return self._protocols[:]
    
    def append_protocol(self, protocol):
        self._protocols.append(protocol)

    @property
    def configurations(self):
        return self._configurations[:]
    
    def append_configuration(self, configuration):
        self._configurations.append(configuration)

    def __repr__(self):
        return "<ServerConfiguration: configurations = %s; type = %s; methods = %s; implementation = %s; protocols = %s>" % (
                    self._configurations,
                    self.server_type,
                    self.methods,
                    self.implementation,
                    self._protocols
                )

class InstanceConfiguration(object):
    def __init__(self, address, configurations, servers):
        super(InstanceConfiguration, self).__init__()
        self.address         = address
        self._configurations = configurations
        self._servers        = servers
        self.user            = None

    @property
    def servers(self):
        return self._servers.copy()

    def append_server(self, server):
        self._servers.append(server)

    @property
    def configurations(self):
        return self._configurations[:]

    def append_configuration(self, configuration):
        self._configurations.append(configuration)

    def __repr__(self):
        return "<InstanceConfiguration: configurations = %s; servers = %s>" % (self._configurations, self._servers)

class MachineConfiguration(object):
    def __init__(self, address, configurations, instances):
        super(MachineConfiguration, self).__init__()
        self.address         = address
        self._configurations = configurations
        self._instances      = instances

    @property
    def instances(self):
        return self._instances.copy()

    @property
    def configurations(self):
        return self._configurations[:]

    def __repr__(self):
        return "<MachineConfiguration: configurations = %s; instances = %s>" % (self._configurations, self._instances)

class GlobalConfiguration(object):
    def __init__(self, address, configurations, machines):
        super(GlobalConfiguration, self).__init__()
        self._configurations = configurations
        self._machines       = machines

    @property
    def machines(self):
        return self._machines.copy()

    @property
    def configurations(self):
        return self._configurations[:]

    def __repr__(self):
        return "<GlobalConfiguration: configurations = %s; machines = %s>" % (self._configurations, self._machines)

