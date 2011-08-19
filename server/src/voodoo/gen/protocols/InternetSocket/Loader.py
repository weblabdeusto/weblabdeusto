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

import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.protocols.InternetSocket.Address as Address
import voodoo.gen.exceptions.loader.LoaderExceptions as LoaderExceptions

# TODO: test me

def fill_coordinations(coordinations_configuration, address):
    coordinations = []
    for coordination_configuration in coordinations_configuration.coordinations:
        if len(coordination_configuration.parameters) != 1:
            raise LoaderExceptions.InvalidConfigurationException(
                    "Unexpected number of parameters for InternetSocket coordinations, expected 1 and received %s" % len(coordination_configuration.parameters)
                )
        parameter = coordination_configuration.parameters[0]
        if parameter.name != 'address':
            raise LoaderExceptions.InvalidConfigurationException(
                    "Parameter for InternetSocket coordinations should be address, found %s" % parameter.name
                )
        try:
            address = Address.Address(parameter.value)
        except Exception as e:
            raise LoaderExceptions.InvalidConfigurationException(
                    "Invalid address format for InternetSocket coordinations: %s" % e
                )
        coordinations.append(address)
    coordinations_configuration.filled_coordinations = coordinations
    coordinations_configuration.filled_level = AccessLevel.network

def fill_creation(protocol_configuration, coord_address):
    creation_configuration = protocol_configuration.creation
    if len(creation_configuration.parameters) != 2:
        raise LoaderExceptions.InvalidConfigurationException(
                "Unexpected number of parameters for InternetSocket creation, expected 2 and received %s" % len(creation_configuration.parameters)
            )

    if creation_configuration.parameters[0].name == 'address':
        address = creation_configuration.parameters[0].value
    elif creation_configuration.parameters[1].name == 'address':
        address = creation_configuration.parameters[1].value
    else:
        raise LoaderExceptions.InvalidConfigurationException(
                "Parameter 'address' not found in InternetSocket creation"
            )
    if creation_configuration.parameters[0].name == 'port':
        port_value = creation_configuration.parameters[0].value
    elif creation_configuration.parameters[1].name == 'port':
        port_value = creation_configuration.parameters[1].value
    else:
        raise LoaderExceptions.InvalidConfigurationException(
                "Parameter 'port' not found in InternetSocket creation"
            )

    try:
        port_number = int(port_value)
    except ValueError:
        raise LoaderExceptions.InvalidConfigurationException(
                'Invalid port: %s' % port_value
            )
    else:
        if port_number > 65536 or port_number < 0:
            raise LoaderExceptions.InvalidConfigurationException(
                    'Invalid port: %s' % port_value
                )

    protocol_configuration.filled_creation = ('InternetSocket',(address,port_number), {})


