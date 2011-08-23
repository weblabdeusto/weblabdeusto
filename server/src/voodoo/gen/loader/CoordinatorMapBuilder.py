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

import voodoo.gen.coordinator.Access  as Access
import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.coordinator.CoordinationInformation as CoordInfo
import voodoo.gen.protocols as protocol_pkg

class CoordinatorMapBuilder(object):
    def _fill_server(self, map, server, machine_name, instance_name, server_name):
        for protocol in server.protocols:
            protocol_module = getattr(protocol_pkg,protocol.name)
            __import__(protocol_module.__name__ + '.Network', globals(), locals())
            NetworkClass = getattr(protocol_module.Network, "%sNetwork" % protocol.name)
            networks = []
            for address in protocol.coordinations.filled_coordinations:
                network = NetworkClass(address)
                networks.append(network)
            
            access = Access.Access(
                    getattr(Protocols, protocol.name),
                    protocol.coordinations.filled_level,
                    tuple(networks)
                )
            map.append_accesses(
                    machine_name,
                    instance_name,
                    server_name,
                    (access,)
                )

    def _fill_instance(self, map, instance_configuration, machine_name, instance_name):
        for server_name in instance_configuration.servers.keys():
            server = instance_configuration.servers[server_name]
            map.add_new_server(
                    machine_name,
                    instance_name,
                    server_name,
                    server.server_type,
                    (),
                    tuple(server.restrictions)
                )
            self._fill_server(
                    map,
                    server,
                    machine_name,
                    instance_name,
                    server_name
                )

    def _fill_machine (self, map, machine_configuration,  machine_name):
        for instance_name in machine_configuration.instances.keys():
            map.add_new_instance(machine_name, instance_name)
            self._fill_instance(
                    map, 
                    machine_configuration.instances[instance_name],
                    machine_name,
                    instance_name
                )

    def build(self, global_configuration):
        map = CoordInfo.CoordinationMap()

        for machine_name in global_configuration.machines.keys():
            map.add_new_machine(machine_name)
            self._fill_machine(
                    map, 
                    global_configuration.machines[machine_name],
                    machine_name
                )
        return map

