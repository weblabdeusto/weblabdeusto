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

import os
import xml.dom.minidom as minidom

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.protocols as protocols_package
import voodoo.gen.exceptions.loader.LoaderErrors as LoaderErrors
import voodoo.gen.loader.ConfigurationData as ConfigurationData
import voodoo.gen.loader.schema_checker as SchemaChecker
import voodoo.gen.loader.util as LoaderUtilities

SERVER_XSD_FILE_PATH   = 'server_configuration.xsd'
INSTANCE_XSD_FILE_PATH = 'instance_configuration.xsd'
MACHINE_XSD_FILE_PATH  = 'machine_configuration.xsd'
GLOBAL_XSD_FILE_PATH   = 'global_configuration.xsd'

class AbstractParser(object):
    def _retrieve_stream(self, directory):
        file_path = os.sep.join((directory,'configuration.xml'))
        try:
            return open(file_path), file_path
        except Exception as e:
            raise LoaderErrors.InvalidConfigurationError("Couldn't parse '%s': %s" % (file_path,e))

    def parse(self, directory, address = None):
        if not isinstance(self, GlobalParser) and address is None:
            raise LoaderErrors.InvalidConfigurationError( "Missing address parameter" )
        stream, file_path = self._retrieve_stream(directory)
        return self._parse_from_stream(stream, directory, file_path, address)

    def _parse_dom(self, stream, file_path):
        try:
            return minidom.parse(stream)
        except Exception as e:
            raise LoaderErrors.InvalidConfigurationError("Couldn't load xml file %s: %s" % (file_path, e))

    def _parse_configurations(self, directory, configuration_nodes):
        configurations = []
        for configuration_node in configuration_nodes:
            relative_file = configuration_nodes[0].getAttribute('file')
            configurations.append(
                os.path.join(directory,relative_file)
            )

        return configurations

class ServerParser(AbstractParser):

    def _parse_from_stream(self, stream, directory, file_path, address):
        server_dom = self._parse_dom(stream, file_path)

        # Check schema
        schema_checker     = SchemaChecker.SchemaChecker()
        schema_checker.check_schema(file_path, SERVER_XSD_FILE_PATH)

        server_node         = LoaderUtilities.find_node(file_path, server_dom,  'server')

        # Load important nodes
        configuration_nodes = LoaderUtilities.find_nodes(file_path, server_node,  'configuration')
        server_type_node    = LoaderUtilities.find_node(file_path, server_node, 'type')
        methods_node        = LoaderUtilities.find_node(file_path, server_node, 'methods')
        implementation_node = LoaderUtilities.find_node(file_path, server_node, 'implementation')
        restrictions_nodes  = LoaderUtilities.find_nodes(file_path, server_node,  'restriction')
        protocols_nodes     = LoaderUtilities.find_node(file_path, server_node, 'protocols')

        # Parse nodes
        configurations     = self._parse_configurations(directory, configuration_nodes)
        server_type        = self._parse_server_type(server_type_node)
        server_type_module = self._parse_server_type_module(server_type_node)
        methods            = self._parse_methods(methods_node)
        implementation     = self._parse_implementation(implementation_node)
        restrictions       = self._parse_restrictions(directory, restrictions_nodes)
        protocols          = self._parse_protocols(file_path, protocols_nodes, address)

        # Return structure
        server_configuration = ConfigurationData.ServerConfiguration(
                    None,
                    configurations,
                    server_type,
                    server_type_module,
                    methods,
                    implementation,
                    restrictions,
                    protocols
                )
        return server_configuration

    def _parse_server_type(self, server_type_node):
        return self._retrieve_variable(server_type_node)

    def _parse_server_type_module(self, server_type_node):
        text_value = LoaderUtilities.obtain_text_safe(server_type_node)
        if text_value.count('::') != 1:
            raise LoaderErrors.InvalidConfigurationError(
                        'Unknown format: %s. module::variable expected' % text_value
                    )

        module_name, _ = text_value.split('::')
        module_inst = LoaderUtilities.obtain_from_python_path(module_name)
        return module_inst

    def _parse_methods(self, methods_node):
        return self._retrieve_variable(methods_node)

    def _retrieve_variable(self, format_node):
        text_value = LoaderUtilities.obtain_text_safe(format_node)
        if text_value.count('::') != 1:
            raise LoaderErrors.InvalidConfigurationError(
                        'Unknown format: %s. module::variable expected' % text_value
                    )

        module_name, variable = text_value.split('::')
        module_inst = LoaderUtilities.obtain_from_python_path(module_name)
        try:
            return getattr(module_inst, variable)
        except AttributeError:
            raise LoaderErrors.InvalidConfigurationError(
                    'Unknown format: couldn\'t find %s in %s' % (variable, module_name)
                )

    def _parse_implementation(self, implementation_node):
        implementation_class_name = LoaderUtilities.obtain_text_safe(implementation_node)
        return LoaderUtilities.obtain_from_python_path(implementation_class_name)

    def _parse_restrictions(self, directory, restriction_nodes):
        restrictions = []
        for restrictions_node in restriction_nodes:
            restriction = LoaderUtilities.obtain_text_safe(restrictions_node)
            restrictions.append(
                restriction
            )

        return restrictions

    def _parse_protocols(self, file_path, protocols_node, address):
        protocol_nodes = [ node
                for node in protocols_node.childNodes
                    if isinstance(node, minidom.Element)
            ]
        protocols = []
        for protocol_node in protocol_nodes:
            protocol = self._parse_protocol(file_path, protocol_node, address)
            protocols.append(protocol)
        return protocols

    def _parse_protocol(self, file_path, protocol_node, address):
        protocol_name = protocol_node.getAttribute('name')
        __import__(protocols_package.__name__ + '.' + protocol_name, globals(), locals())
        protocol_pkg = getattr(protocols_package, protocol_name)

        coordinations = self._parse_coordinations(file_path, protocol_node)
        creation = self._parse_creation(file_path, protocol_node)

        __import__(protocol_pkg.__name__ + '.Loader', globals(), locals())
        protocol_pkg.Loader.fill_coordinations( coordinations, address)

        protocol_configuration = ConfigurationData.ProtocolConfiguration(
                protocol_name,
                coordinations,
                creation
            )

        protocol_pkg.Loader.fill_creation(      protocol_configuration, address)
        return protocol_configuration

    def _parse_coordinations(self, file_path, protocol_node):
        coordinations_node = LoaderUtilities.find_node(file_path, protocol_node, 'coordinations')

        coordinations = []
        coordination_nodes = LoaderUtilities.find_nodes(file_path, coordinations_node, 'coordination')
        for coordination_node in coordination_nodes:
            parameters = self._parse_parameters(file_path, coordination_node)
            coordination = ConfigurationData.CoordinationConfiguration(parameters)
            coordinations.append(coordination)

        coordinations_configuration = ConfigurationData.CoordinationsConfiguration(
                coordinations
            )
        return coordinations_configuration

    def _parse_parameters(self, file_path, parameterized_node):
        parameter_nodes = LoaderUtilities.find_nodes(file_path, parameterized_node, 'parameter')
        parameters = []
        for parameter_node in parameter_nodes:
            name  = parameter_node.getAttribute('name')
            value = parameter_node.getAttribute('value')
            parameter = ConfigurationData.ParameterConfiguration(name, value)
            parameters.append(parameter)

        return parameters

    def _parse_creation(self, file_path, protocol_node):
        creation_node = LoaderUtilities.find_node(file_path, protocol_node, 'creation')
        parameters    = self._parse_parameters(file_path, creation_node)
        creation_configuration = ConfigurationData.CreationConfiguration(
                parameters
            )
        return creation_configuration

class AbstractConfigPlusLevelParser(AbstractParser):
    # level = instance / machine / global
    # sub_level: instance => server; machine => instance; global => machine
    def _parse_from_stream(self, stream, directory, file_path, address):
        level_dom = self._parse_dom(stream, file_path)

        # Check schema
        schema_checker      = SchemaChecker.SchemaChecker()
        schema_checker.check_schema(file_path, self.XSD_FILE_PATH)

        level_node      = LoaderUtilities.find_node(file_path, level_dom,  self.SUB_LEVEL + 's')

        # Load important nodes
        configuration_nodes = LoaderUtilities.find_nodes(file_path, level_node,  'configuration')
        user_nodes          = LoaderUtilities.find_nodes(file_path, level_node,  'user')
        runner_nodes        = LoaderUtilities.find_nodes(file_path, level_node,  'runner')
        sub_level_nodes     = LoaderUtilities.find_nodes(file_path, level_node, self.SUB_LEVEL)

        # Parse nodes
        configurations      = self._parse_configurations(directory, configuration_nodes)
        runner              = self._parse_runner(directory, runner_nodes)
        sub_levels          = self._parse_level(address, directory, sub_level_nodes)

        # Return structure
        level_configuration = self.CONFIG_CLASS(
                    None,
                    configurations,
                    sub_levels,
                    runner = runner,
                )

        # We know there can be 0 or 1 node...
        if len(user_nodes) > 0:
            level_configuration.user = LoaderUtilities.obtain_text_safe(user_nodes[0])

        return level_configuration

    def _parse_runner(self, directory, runner_nodes):
        if len(runner_nodes) == 0:
            return None
        else:
            return os.path.relpath(os.path.join(directory, '..', runner_nodes[0].getAttribute('file')))

    def _parse_level(self, address, directory, sub_level_nodes):
        sub_level_names = [
                LoaderUtilities.obtain_text_safe(sub_level_node)
                for sub_level_node in sub_level_nodes
            ]

        sub_level_parser = self.PARSER()
        sub_levels_configurations = {}

        for sub_level_name in sub_level_names:
            sub_level_directory = os.sep.join((directory, sub_level_name))
            parsed_sub_level = sub_level_parser.parse(
                    sub_level_directory,
                    self._generate_address_of_sublevel(
                        address,
                        sub_level_name
                    )
                )
            sub_levels_configurations[sub_level_name] = parsed_sub_level

        return sub_levels_configurations

class InstanceParser(AbstractConfigPlusLevelParser):
    CONFIG_CLASS  = ConfigurationData.InstanceConfiguration
    XSD_FILE_PATH = INSTANCE_XSD_FILE_PATH
    SUB_LEVEL     = 'server'
    PARSER        = ServerParser

    def _generate_address_of_sublevel(self, address, name):
        return CoordAddress.CoordAddress( address.machine_id, address.instance_id, name )


class MachineParser(AbstractConfigPlusLevelParser):
    CONFIG_CLASS  = ConfigurationData.MachineConfiguration
    XSD_FILE_PATH = MACHINE_XSD_FILE_PATH
    SUB_LEVEL     = 'instance'
    PARSER        = InstanceParser

    def _generate_address_of_sublevel(self, address, name):
        return CoordAddress.CoordAddress( address.machine_id, name )

class GlobalParser(AbstractConfigPlusLevelParser):
    CONFIG_CLASS  = ConfigurationData.GlobalConfiguration
    XSD_FILE_PATH = GLOBAL_XSD_FILE_PATH
    SUB_LEVEL     = 'machine'
    PARSER        = MachineParser

    def _generate_address_of_sublevel(self, address, name):
        return CoordAddress.CoordAddress( name )

