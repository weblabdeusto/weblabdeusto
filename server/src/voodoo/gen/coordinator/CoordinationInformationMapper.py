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
# Right now we use pickle 0:-)

import pickle
import voodoo.mapper as mapper

import voodoo.gen.exceptions.coordinator.CoordMappingExceptions as CoordMapExceptions

def dump_to_file(coordination_map,file):
    try:
        dto_object = mapper.dto_generator(coordination_map)
    except Exception as e:
        raise CoordMapExceptions.CoordSerializingException(
                "Exception <%s> caught serializing coordination_map <%s>"
                % (e,coordination_map),
                e
            )
    try:
        pickle.dump(dto_object,file)
    except Exception as e:
        raise CoordMapExceptions.CoordDumpingException(
                "Exception <%s> caught dumping coordination_map <%s> to file <%s>"
                % (e,coordination_map,file),
                e
            )

def load_from_file(file):
    try:
        dto_object = pickle.load(file)
    except Exception as e:
        raise CoordMapExceptions.CoordLoadingException(
                "Exception <%s> caught loading coordmap from file <%s>"
                % (e,file),
                e
            )
    try:
        dto_object = mapper.load_from_dto(dto_object)
    except Exception as e:
        raise CoordMapExceptions.CoordLoadingException(
                "Exception <%s> caught deserializing dto_object <%s> received from file <%s>"
                % (e,dto_object,file),
                e
            )

    return dto_object

