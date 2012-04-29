#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import voodoo.methods as voodoo_exported_methods

import voodoo.configuration as ConfigurationManager

import voodoo.gen.loader.ConfigurationParser as ConfigurationParser
import voodoo.gen.loader.CoordinatorMapBuilder as CoordinatorMapBuilder

import voodoo.gen.protocols.protocols as Protocols
import voodoo.gen.protocols.Direct.network as DirectNetwork
import voodoo.gen.protocols.Direct.Address as DirectAddress

import voodoo.gen.generators.ServerSkel as ServerSkel

import voodoo.gen.locator.ServerTypeHandler as ServerTypeHandler
import voodoo.gen.locator.ServerLocator as ServerLocator
import voodoo.gen.locator.EasyLocator as EasyLocator

import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.coordinator.Access as Access
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.coordinator.CoordinatorServer as CoordinatorServer

class InstanceHandler(object):
    def __init__(self, started_servers):
        self.started_servers = started_servers

    def stop(self):
        for server in self.started_servers:
            server.stop()

class ServerLoader(object):
    def load_instance(self, global_folder, machine_name, instance_name):
        global_parser = ConfigurationParser.GlobalParser()
        global_configuration = global_parser.parse(global_folder)

        if (
                not global_configuration.machines.has_key(machine_name)
                or
                not global_configuration.machines[machine_name].instances.has_key(instance_name)
            ):
            raise Exception("instance@machine not found")

        if len(global_configuration.machines[machine_name].instances[instance_name].servers.keys()) == 0:
            raise Exception("Zero servers found!")

        self._create_coordinator_server(
                global_configuration,
                machine_name,
                instance_name
            )

        machine  = global_configuration.machines[machine_name]
        instance = machine.instances[instance_name]
        started_servers = []
        for server_name in instance.servers:
            locator = self._generate_easy_locator(
                    global_configuration,
                    machine_name,
                    instance_name,
                    server_name
                )

            cfg_manager = self._create_config_manager(
                    global_configuration,
                    machine_name,
                    instance_name,
                    server_name
                )
            started_server = self._create_server(
                    global_configuration,
                    machine_name,
                    instance_name,
                    server_name,
                    locator,
                    cfg_manager
                )
            started_servers.append(started_server)

        return InstanceHandler(started_servers)

    def _create_config_manager_for_instance(self, global_config, machine_name, instance_name):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        for cfg_file_name in global_config.configurations:
            cfg_manager.append_path(cfg_file_name)

        for cfg_file_name in global_config.machines[machine_name].configurations:
            cfg_manager.append_path(cfg_file_name)
        for cfg_file_name in global_config.machines[machine_name].instances[instance_name].configurations:
            cfg_manager.append_path(cfg_file_name)
        return cfg_manager

    def _create_config_manager(self, global_config, machine_name, instance_name, server_name):
        cfg_manager = self._create_config_manager_for_instance(global_config, machine_name, instance_name)
        for configuration in global_config.machines[machine_name].instances[instance_name].servers[server_name].configurations:
            cfg_manager.append_path(configuration)
        return cfg_manager

    def _create_coordinator_server(self, global_config, machine_name, instance_name):
        map_builder = CoordinatorMapBuilder.CoordinatorMapBuilder()
        map = map_builder.build(global_config)

        coordinator_server_name = self._generate_coordinator_server_name(
                    machine_name,
                    instance_name
                )

        any_server = global_config.machines[machine_name].instances[instance_name].servers.values()[0]

        server_type = getattr(any_server.server_type_module,'Coordinator')

        map.add_new_server(
                machine_name,
                instance_name,
                coordinator_server_name,
                server_type,
                (),
                ()
            )

        coordinator_coord_address = map[machine_name][instance_name][coordinator_server_name].address
        coordinator_network = DirectNetwork.DirectNetwork(
                DirectAddress.from_coord_address(coordinator_coord_address)
            )
        coordinator_access = Access.Access(
                Protocols.Direct,
                AccessLevel.instance,
                (coordinator_network,)
            )
        map.append_accesses(
                machine_name,
                instance_name,
                coordinator_server_name,
                ( coordinator_access, )
            )

        protocols = (Protocols.Direct,)

        cfg_manager = self._create_config_manager_for_instance(
                global_config,
                machine_name,
                instance_name
            )

        generated_coordinator = ServerSkel.factory(
                    cfg_manager,
                    protocols,
                    voodoo_exported_methods.coordinator
                )

        class RealCoordinatorServer(CoordinatorServer.CoordinatorServer,generated_coordinator):
            def __init__(self,cfg_manager,map,*args,**kargs):
                CoordinatorServer.CoordinatorServer.__init__(self,cfg_manager,map, *args, **kargs)

        real_coordinator_server = RealCoordinatorServer(
                cfg_manager,
                map,
                Direct = (coordinator_coord_address.address,),
            )
        real_coordinator_server.start()
        return real_coordinator_server

    def _generate_easy_locator(self, global_config, machine_name, instance_name, server_name):
        coordinator_server_address = DirectAddress.Address(
                machine_name,
                instance_name,
                self._generate_coordinator_server_name(
                    machine_name,
                    instance_name
                )
            )

        server_type, map = self._generate_map_server_type2methods(global_config)
        server_type_handler = ServerTypeHandler.ServerTypeHandler(
                server_type,
                map
            )

        locator = ServerLocator.ServerLocator(
                coordinator_server_address,
                server_type_handler
            )

        server_coord_address = CoordAddress.CoordAddress(
                machine_name,
                instance_name,
                server_name
            )

        easy_locator = EasyLocator.EasyLocator(
                server_coord_address,
                locator
            )

        return easy_locator

    def _generate_map_server_type2methods(self, global_config):
        current_server_type = None
        map = {}
        for machine in global_config.machines.values():
            for instance in machine.instances.values():
                for server in instance.servers.values():
                    if current_server_type is None:
                        current_server_type = server.server_type_module
                    if current_server_type != server.server_type_module:
                        raise Exception("Too many server types found!")
                    map[server.server_type] = server.methods

        if current_server_type is None:
            raise Exception("No server type found!")
        map[current_server_type.Coordinator] = voodoo_exported_methods.coordinator
        return current_server_type, map

    def _generate_coordinator_server_name(self, machine_name, instance_name):
        return '__%s_%s_coordinator__' % (
                        machine_name,
                        instance_name
                    )

    def _create_server(self, global_config, machine_name, instance_name, server_name, locator, cfg_manager):
        server_config = global_config.machines[machine_name].instances[instance_name].servers[server_name]
        protocols = [ getattr(Protocols,protocol.name) for protocol in server_config.protocols ]
        generated_server = ServerSkel.factory(
                cfg_manager,
                protocols,
                server_config.methods
            )

        class RealServer(server_config.implementation, generated_server):
            def __init__(self, coord_address, locator, cfg_manager,*args,**kargs):
                server_config.implementation.__init__(self, coord_address, locator, cfg_manager, *args, **kargs)

        RealServer.__name__ = 'Server of %s' % server_config.implementation

        coord_address = CoordAddress.CoordAddress(
                    machine_name,
                    instance_name,
                    server_name
                )

        protocol_args = {}
        for protocol in server_config.protocols:
            if isinstance(protocol.name, unicode):
                protocol_name = str(protocol.name)
            else:
                protocol_name = protocol.name
            protocol_args[protocol_name] = protocol.filled_creation[1]

        real_server = RealServer(
                coord_address,
                locator,
                cfg_manager,
                **protocol_args
            )
        real_server.start()
        return real_server

