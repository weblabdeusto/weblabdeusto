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

import voodoo.gen.coordinator.AccessLevel as AccessLevel
import voodoo.gen.protocols.UnixSocket.address as Address
import voodoo.gen.exceptions.loader.LoaderErrors as LoaderErrors

# TODO: test me

def fill_coordinations(coordinations_configuration, address):
    if len(coordinations_configuration.coordinations) != 1:
        raise LoaderErrors.InvalidConfigurationError(
                "Unexpected number of coordinations for UnixSocket, expected 1 and received %s" % len(coordinations_configuration.parameters)
            )

    if len(coordinations_configuration.coordinations[0].parameters) != 1:
        raise LoaderErrors.InvalidConfigurationError(
                "Unexpected number of parameters for UnixSocket coordinations, expected 1 and received %s" % len(coordinations_configuration[0].parameters)
            )

    parameter = coordinations_configuration.coordinations[0].parameters[0]
    if parameter.name != 'sockpath':
        raise LoaderErrors.InvalidConfigurationError(
            "Unexpected parameter: expected 'sockpath' and found:" % parameter.name
        )


    coordinations_configuration.filled_coordinations = [
            Address.Address(address.machine_id, parameter.value)
        ]

    coordinations_configuration.filled_level = AccessLevel.machine

def fill_creation(protocol_configuration, coord_address):
    creation_configuration = protocol_configuration.creation
    if len(creation_configuration.parameters) != 1:
        raise LoaderErrors.InvalidConfigurationError(
                "Unexpected number of parameters for UnixSocket creation, expected 1 and received %s" % len(creation_configuration.parameters)
            )

    if creation_configuration.parameters[0].name == 'socketpath':
        socket_path = creation_configuration.parameters[0].value
    else:
        raise LoaderErrors.InvalidConfigurationError(
                "Parameter 'socketpath' not found in UnixSocket creation"
            )

    protocol_configuration.filled_creation = ('UnixSocket',(socket_path,), {})

