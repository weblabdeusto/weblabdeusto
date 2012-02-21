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

import unittest

import os
import StringIO

import voodoo.gen.coordinator.AccessLevel  as AccessLevel
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.loader.LoaderExceptions as LoaderExceptions
import voodoo.gen.loader.ConfigurationData as ConfigurationData
import voodoo.gen.loader.ConfigurationParser as ConfigurationParser

import test.unit.voodoo.gen.loader.APItype1 as APItype1
import test.unit.voodoo.gen.loader.ServerSample as ServerSample
import test.unit.voodoo.gen.loader.ServerType as ServerType

GLOBAL_PATH   = 'test/deployments/WebLabSkel/'
MACHINE_PATH  = 'test/deployments/WebLabSkel/NAME_OF_MACHINE1/'
INSTANCE_PATH = 'test/deployments/WebLabSkel/NAME_OF_MACHINE1/NAME_OF_INSTANCE1/'
SERVER_PATH   = 'test/deployments/WebLabSkel/NAME_OF_MACHINE1/NAME_OF_INSTANCE1/NAME_OF_SERVER1/'


SERVER_CONFIG_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<server
    xmlns="http://www.weblab.deusto.es/configuration"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"
>
        <configuration file="server_config.py" />
        <configuration file="server_config.py" />

        <type>%(type)s</type>
        <methods>%(methods)s</methods>

        <implementation>%(implementation)s</implementation>
    <restriction>something</restriction>
    <restriction>something else</restriction>
        <protocols>
        <!-- This server supports both Direct calls, as SOAP calls -->
        <protocol name="Direct">
            <coordinations>
                <level>instance</level>
                <coordination></coordination>
            </coordinations>
            <creation></creation>
        </protocol>
        <protocol name="SOAP">
            <coordinations>
                <level>network</level>
                <coordination>
                    <parameter name="address" value="192.168.0.1:8095@LABORATORYNETWORK" />
                </coordination>
                <coordination>
                    <parameter name="address" value="130.206.100.134:8095@INTERNET" />
                </coordination>
            </coordinations>
            <creation>
                <parameter name="address" value=""     />
                <parameter name="port"    value="8095" />
            </creation>
        </protocol>
        </protocols>
</server>
"""

SERVER_VALID_TYPE           = "test.unit.voodoo.gen.loader.ServerType::Login"
SERVER_VALID_METHODS        = "test.unit.voodoo.gen.loader.APItype1::methods"
SERVER_VALID_IMPLEMENTATION = "test.unit.voodoo.gen.loader.ServerSample.Server"

SERVER_ADDRESS   = CoordAddress.CoordAddress(
                'NAME_OF_MACHINE1',
                'NAME_OF_INSTANCE1',
                'NAME_OF_SERVER1'
            )
INSTANCE_ADDRESS   = CoordAddress.CoordAddress(
                'NAME_OF_MACHINE1',
                'NAME_OF_INSTANCE1'
            )
MACHINE_ADDRESS    = CoordAddress.CoordAddress(
                'NAME_OF_MACHINE1'
            )

class ServerParserTestCase(unittest.TestCase):
    def setUp(self):
        self.server_parser = ConfigurationParser.ServerParser()

    def test_address_is_none(self):
        self.assertRaises(
                LoaderExceptions.InvalidConfigurationException,
                self.server_parser.parse,
                SERVER_PATH,
            )

    def test_parse_file_not_found(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser.parse,
            '.',
            SERVER_ADDRESS
        )

    def test_parse_not_an_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                """this is not an xml"""
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + "configuration.xml",
            SERVER_ADDRESS
        )

    def test_parse_invalid_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                """<?xml version="1.0" encoding="utf-8"?>
                <wellformed><butinvalid></butinvalid></wellformed>"""
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + "configuration.xml",
            SERVER_ADDRESS
        )

    def test_parse_invalid_methods_format_two_points_not_found(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                SERVER_CONFIG_SAMPLE % {
                    'type'           : SERVER_VALID_TYPE,
                    'methods'        : SERVER_VALID_METHODS.replace('::',':'),
                    'implementation' : SERVER_VALID_IMPLEMENTATION,
                }
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + 'configuration.xml',
            SERVER_ADDRESS
        )

    def test_parse_invalid_methods_format_methods_does_not_exist_in_module(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                SERVER_CONFIG_SAMPLE % {
                    'type'           : SERVER_VALID_TYPE,
                    'methods'        : SERVER_VALID_METHODS.replace('::methods','::doesnotexist'),
                    'implementation' : SERVER_VALID_IMPLEMENTATION,
                }
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + 'configuration.xml',
            SERVER_ADDRESS
        )

    def test_parse_invalid_server_type_format_two_points_not_found(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                SERVER_CONFIG_SAMPLE % {
                    'type'           : SERVER_VALID_TYPE.replace('::',':'),
                    'methods'        : SERVER_VALID_METHODS,
                    'implementation' : SERVER_VALID_IMPLEMENTATION,
                }
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + 'configuration.xml',
            SERVER_ADDRESS
        )

    def test_parse_invalid_server_type_format_methods_does_not_exist_in_module(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                SERVER_CONFIG_SAMPLE % {
                    'type'           : SERVER_VALID_TYPE.replace('::Login','::doesnotexist'),
                    'methods'        : SERVER_VALID_METHODS,
                    'implementation' : SERVER_VALID_IMPLEMENTATION,
                }
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + 'configuration.xml',
            SERVER_ADDRESS
        )


    def test_parse_invalid_implementation(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.server_parser._parse_from_stream,
            StringIO.StringIO(
                SERVER_CONFIG_SAMPLE % {
                    'type'           : SERVER_VALID_TYPE,
                    'methods'        : SERVER_VALID_METHODS,
                    'implementation' : SERVER_VALID_IMPLEMENTATION[:-2],
                }
            ),
            SERVER_PATH,
            SERVER_PATH + os.sep + 'configuration.xml',
            SERVER_ADDRESS
        )

    def test_check_tests_config(self):
        parsed_server = self.server_parser._parse_from_stream(
                StringIO.StringIO(
                    SERVER_CONFIG_SAMPLE % {
                        'type'           : SERVER_VALID_TYPE,
                        'methods'        : SERVER_VALID_METHODS,
                        'implementation' : SERVER_VALID_IMPLEMENTATION,
                    }
                ),
                SERVER_PATH,
                SERVER_PATH + os.sep + 'configuration.xml',
                SERVER_ADDRESS
            )
        self._real_test_results(parsed_server)

    def test_parse_complete(self):
        parsed_server = self.server_parser.parse(
                SERVER_PATH,
                SERVER_ADDRESS
            )
        self._real_test_results(parsed_server)

    def _real_test_results(self, parsed_server):
        self.assertEquals(
                2,
                len(parsed_server.configurations)
            )
        self.assertEquals(
                SERVER_PATH + u'server_config.py',
                parsed_server.configurations[0]
            )
        self.assertEquals(
                SERVER_PATH + u'server_config.py',
                parsed_server.configurations[1]
            )
        self.assertEquals(
                APItype1.methods,
                parsed_server.methods
            )
        self.assertEquals(
                ServerSample.Server,
                parsed_server.implementation
            )
        self.assertEquals(
                ServerType.Login,
                parsed_server.server_type
            )
        self.assertEquals(
                2,
                len(parsed_server.restrictions)
            )
        self.assertEquals(
                u'something',
                parsed_server.restrictions[0]
            )
        self.assertEquals(
                u'something else',
                parsed_server.restrictions[1]
            )
        self.assertEquals(
                2,
                len(parsed_server.protocols)
            )

        # Protocol A
        protocolA = parsed_server.protocols[0]

        self.assertEquals(
                AccessLevel.instance,
                protocolA.coordinations.filled_level
            )

        self.assertEquals(
                1,
                len(protocolA.coordinations.coordinations)
            )
        self.assertEquals(
                0,
                len(protocolA.coordinations.coordinations[0].parameters)
            )
        self.assertEquals(
                0,
                len(protocolA.creation.parameters)
            )

        # Protocol B

        protocolB = parsed_server.protocols[1]

        self.assertEquals(
                AccessLevel.network,
                protocolB.coordinations.filled_level
            )

        self.assertEquals(
                2,
                len(protocolB.coordinations.coordinations)
            )
        self.assertEquals(
                1,
                len(protocolB.coordinations.coordinations[0].parameters)
            )
        self.assertEquals(
                "address",
                protocolB.coordinations.coordinations[1].parameters[0].name
            )

        self.assertEquals(
                "192.168.0.1:8095@LABORATORYNETWORK",
                protocolB.coordinations.coordinations[0].parameters[0].value
            )

        self.assertEquals(
                1,
                len(protocolB.coordinations.coordinations[1].parameters)
            )

        self.assertEquals(
                "address",
                protocolB.coordinations.coordinations[1].parameters[0].name
            )

        self.assertEquals(
                "130.206.100.134:8095@INTERNET",
                protocolB.coordinations.coordinations[1].parameters[0].value
            )

        self.assertEquals(
                2,
                len(protocolB.creation.parameters)
            )
        self.assertEquals(
                "address",
                protocolB.creation.parameters[0].name
            )
        self.assertEquals(
                "",
                protocolB.creation.parameters[0].value
            )
        self.assertEquals(
                "port",
                protocolB.creation.parameters[1].name
            )
        self.assertEquals(
                "8095",
                protocolB.creation.parameters[1].value
            )


INSTANCE_CONFIG_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<servers
        xmlns="http://www.weblab.deusto.es/configuration"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="instance_configuration.xsd"
>
        <!-- You can even put more than one (or none) -->
        <configuration file="instance_config.py"/>
        <configuration file="instance_config.py"/>

        <user>weblab</user>

        <server>%(server)s</server>
        <server>NAME_OF_SERVER2</server>
</servers>
"""

class InstanceParserTestCase(unittest.TestCase):
    def setUp(self):
        self.instance_parser = ConfigurationParser.InstanceParser()

    def test_address_is_none(self):
        self.assertRaises(
                LoaderExceptions.InvalidConfigurationException,
                self.instance_parser.parse,
                INSTANCE_PATH,
            )

    def test_parse_not_an_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.instance_parser._parse_from_stream,
            StringIO.StringIO(
                """this is not an xml"""
            ),
            INSTANCE_PATH,
            INSTANCE_PATH + os.sep + "configuration.xml",
            INSTANCE_ADDRESS
        )

    def test_parse_invalid_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            self.instance_parser._parse_from_stream,
            StringIO.StringIO(
                """<?xml version="1.0" encoding="utf-8"?>
                <wellformed><butinvalid></butinvalid></wellformed>"""
            ),
            INSTANCE_PATH,
            INSTANCE_PATH + os.sep + "configuration.xml",
            INSTANCE_ADDRESS
        )

    def test_parse_invalid_server(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.instance_parser._parse_from_stream,
            StringIO.StringIO(
                INSTANCE_CONFIG_SAMPLE % {
                        'server' : 'THIS.SERVER.DOES.NOT.EXIST'
                    }
            ),
            INSTANCE_PATH,
            INSTANCE_PATH + os.sep + "configuration.xml",
            INSTANCE_ADDRESS
        )

    def test_check_tests_config(self):
        parsed_instance = self.instance_parser._parse_from_stream(
                StringIO.StringIO(
                    INSTANCE_CONFIG_SAMPLE % {
                        'server' : 'NAME_OF_SERVER1'
                    }
                ),
                INSTANCE_PATH,
                INSTANCE_PATH + os.sep + 'configuration.xml',
                INSTANCE_ADDRESS
            )
        self._real_test_results(parsed_instance, "weblab")

    def test_parse(self):
        parsed_instance = self.instance_parser.parse(
                INSTANCE_PATH,
                INSTANCE_ADDRESS
            )
        self._real_test_results(parsed_instance, None)

    def _real_test_results(self, parsed_instance, user):
        self.assertEquals(
                2,
                len(parsed_instance.configurations)
            )
        self.assertEquals(
                user,
                parsed_instance.user
            )
        self.assertEquals(
                INSTANCE_PATH + u'instance_config.py',
                parsed_instance.configurations[0]
            )
        self.assertEquals(
                INSTANCE_PATH + u'instance_config.py',
                parsed_instance.configurations[1]
            )
        self.assertTrue(
                isinstance(
                    parsed_instance.servers[u'NAME_OF_SERVER1'],
                    ConfigurationData.ServerConfiguration
                )
            )
        self.assertTrue(
                isinstance(
                    parsed_instance.servers[u'NAME_OF_SERVER2'],
                    ConfigurationData.ServerConfiguration
                )
            )

MACHINE_CONFIG_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<instances
        xmlns="http://www.weblab.deusto.es/configuration"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="machine_configuration.xsd"
>
        <!-- You can even put more than one (or none) -->
        <configuration file="machine_config.py"/>
        <configuration file="machine_config.py"/>

        <instance>%(instance)s</instance>
        <instance>NAME_OF_INSTANCE2</instance>
</instances>
"""
class MachineParserTestCase(unittest.TestCase):
    def setUp(self):
        self.machine_parser = ConfigurationParser.MachineParser()

    def test_address_is_none(self):
        self.assertRaises(
                LoaderExceptions.InvalidConfigurationException,
                self.machine_parser.parse,
                MACHINE_PATH,
            )

    def test_parse_not_an_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.machine_parser._parse_from_stream,
            StringIO.StringIO(
                """this is not an xml"""
            ),
            MACHINE_PATH,
            MACHINE_PATH + os.sep + "configuration.xml",
            MACHINE_ADDRESS
        )

    def test_parse_invalid_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            self.machine_parser._parse_from_stream,
            StringIO.StringIO(
                """<?xml version="1.0" encoding="utf-8"?>
                <wellformed><butinvalid></butinvalid></wellformed>"""
            ),
            MACHINE_PATH,
            MACHINE_PATH + os.sep + "configuration.xml",
            MACHINE_ADDRESS
        )

    def test_parse_invalid_server(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.machine_parser._parse_from_stream,
            StringIO.StringIO(
                MACHINE_CONFIG_SAMPLE % {
                        'instance' : 'THIS.INSTANCE.DOES.NOT.EXIST'
                    }
            ),
            MACHINE_PATH,
            MACHINE_PATH + os.sep + "configuration.xml",
            MACHINE_ADDRESS
        )

    def test_check_tests_config(self):
        parsed_machine = self.machine_parser._parse_from_stream(
                StringIO.StringIO(
                    MACHINE_CONFIG_SAMPLE % {
                        'instance' : 'NAME_OF_INSTANCE1'
                    }
                ),
                MACHINE_PATH,
                MACHINE_PATH + os.sep + 'configuration.xml',
                MACHINE_ADDRESS
            )
        self._real_test_results(parsed_machine)

    def test_parse(self):
        parsed_machine = self.machine_parser.parse(
                MACHINE_PATH,
                MACHINE_ADDRESS
            )
        self._real_test_results(parsed_machine)

    def _real_test_results(self, parsed_machine):
        self.assertEquals(
                2,
                len(parsed_machine.configurations)
            )
        self.assertEquals(
                MACHINE_PATH + u'machine_config.py',
                parsed_machine.configurations[0]
            )
        self.assertEquals(
                MACHINE_PATH + u'machine_config.py',
                parsed_machine.configurations[1]
            )
        self.assertTrue(
                isinstance(
                    parsed_machine.instances[u'NAME_OF_INSTANCE1'],
                    ConfigurationData.InstanceConfiguration
                )
            )
        self.assertTrue(
                isinstance(
                    parsed_machine.instances[u'NAME_OF_INSTANCE2'],
                    ConfigurationData.InstanceConfiguration
                )
            )

GLOBAL_CONFIG_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<machines
        xmlns="http://www.weblab.deusto.es/configuration"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="global_configuration.xsd"
>
        <!-- You can even put more than one (or none) -->
        <configuration file="global_config.py"/>
        <configuration file="global_config.py"/>

        <machine>%(machine)s</machine>
</machines>
"""
class GlobalParserTestCase(unittest.TestCase):
    def setUp(self):
        self.global_parser = ConfigurationParser.GlobalParser()

    def test_parse_not_an_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.global_parser._parse_from_stream,
            StringIO.StringIO(
                """this is not an xml"""
            ),
            GLOBAL_PATH,
            GLOBAL_PATH + os.sep + "configuration.xml",
            None
        )

    def test_parse_invalid_xml(self):
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            self.global_parser._parse_from_stream,
            StringIO.StringIO(
                """<?xml version="1.0" encoding="utf-8"?>
                <wellformed><butinvalid></butinvalid></wellformed>"""
            ),
            GLOBAL_PATH,
            GLOBAL_PATH + os.sep + "configuration.xml",
            None
        )

    def test_parse_invalid_server(self):
        self.assertRaises(
            LoaderExceptions.InvalidConfigurationException,
            self.global_parser._parse_from_stream,
            StringIO.StringIO(
                GLOBAL_CONFIG_SAMPLE % {
                        'machine' : 'THIS.MACHINE.DOES.NOT.EXIST'
                    }
            ),
            GLOBAL_PATH,
            GLOBAL_PATH + os.sep + "configuration.xml",
            None
        )

    def test_check_tests_config(self):
        parsed_global = self.global_parser._parse_from_stream(
                StringIO.StringIO(
                    GLOBAL_CONFIG_SAMPLE % {
                        'machine' : 'NAME_OF_MACHINE1'
                    }
                ),
                GLOBAL_PATH,
                GLOBAL_PATH + os.sep + 'configuration.xml',
                None
            )
        self._real_test_results(parsed_global)

    def test_parse(self):
        parsed_global = self.global_parser.parse(
                GLOBAL_PATH
            )
        self._real_test_results(parsed_global)

    def _real_test_results(self, parsed_global):
        self.assertEquals(
                2,
                len(parsed_global.configurations)
            )
        self.assertEquals(
                GLOBAL_PATH + u'global_config.py',
                parsed_global.configurations[0]
            )
        self.assertEquals(
                GLOBAL_PATH + u'global_config.py',
                parsed_global.configurations[1]
            )
        self.assertTrue(
                isinstance(
                    parsed_global.machines[u'NAME_OF_MACHINE1'],
                    ConfigurationData.MachineConfiguration
                )
            )

def suite():
    return unittest.TestSuite(
        (
            unittest.makeSuite(ServerParserTestCase),
            unittest.makeSuite(InstanceParserTestCase),
            unittest.makeSuite(MachineParserTestCase),
            unittest.makeSuite(GlobalParserTestCase),
        )
    )

if __name__ == '__main__':
    unittest.main()

