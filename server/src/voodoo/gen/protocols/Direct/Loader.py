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
import voodoo.gen.protocols.Direct.Address as Address
import voodoo.gen.exceptions.loader.LoaderErrors as LoaderErrors

# TODO: test me

def fill_coordinations(coordinations_configuration, address):
    if len(coordinations_configuration.coordinations) != 1:
        raise LoaderErrors.InvalidConfigurationError(
                "Unexpected number of coordinations for Direct, expected 1 and received %s" % len(coordinations_configuration.parameters)
            )

    if len(coordinations_configuration.coordinations[0].parameters) != 0:
        raise LoaderErrors.InvalidConfigurationError(
                "Unexpected number of parameters for Direct coordinations, expected 0 and received %s" % len(coordinations_configuration[0].parameters)
            )
    coordinations_configuration.filled_coordinations = [
            Address.from_coord_address(address)
        ]
    coordinations_configuration.filled_level = AccessLevel.instance

def fill_creation(protocol_configuration, address):
    creation_configuration = protocol_configuration.creation
    if len(creation_configuration.parameters) != 0:
        raise LoaderErrors.InvalidConfigurationError(
                "Unexpected number of parameters for Direct creation, expected 0 and received %s" % len(creation_configuration.parameters)
            )

    protocol_configuration.filled_creation = ('Direct',(address.address,), {})


