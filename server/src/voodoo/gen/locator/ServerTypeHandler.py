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
import voodoo.abstraction.enumeration as enumeration

import voodoo.gen.exceptions.locator.LocatorExceptions as LocatorExceptions

class ServerTypeHandler(object):
    def __init__(self,server_type_type, methods):
        """ server_type_type is a Enumeration-created type.

        For example: voodoo.gen.protocols.Protocols.Protocols
        (not voodoo.gen.protocols.Protocols, that's only a module).

        The second parameter, "methods", must be a dictionary like:
        {
            EnumerationMember1Name : 'method_name1',
            EnumerationMember2Name : 'method_name2',
            ...
        }
        """
        self._inspected_type = enumeration.inspectEnumeration(server_type_type)
        self._name = self._inspected_type['name']
        self._module = self._inspected_type['module']

        self._methods = self._generate_methods(methods)
        

    def _generate_methods(self,methods):
        returnValue = {}

        possible_server_type_names = [ value.name for value in self.getValues() ]

        for i in possible_server_type_names:
            if methods.has_key(i):
                method_names = methods[i]
                if not isinstance(method_names,tuple) and not isinstance(method_names,list):
                    raise LocatorExceptions.InvalidListOfMethodsException(
                            "Server %s does not have a valid sequence of methods" % i
                        )
                else:
                    returnValue[i] = methods[i]

        for method in methods:
            if method not in possible_server_type_names:
                raise LocatorExceptions.MoreServersThanExpectedException(
                        'More servers than keys found in %s' % methods
                    )

        return returnValue
    
    def retrieve_methods(self,server_type):
        if self._methods.has_key(server_type):
            return self._methods[server_type]
        else:
            raise LocatorExceptions.NoSuchServerTypeFoundException(
                    "Server type '%s' not found retrieving methods" % server_type
                )

    @property
    def name(self):
        return self._name

    @property
    def module(self):
        return self._module


    def getValues(self):
        return self._inspected_type['getValues']()

    def isMember(self, obj):
        return self._inspected_type['is'](obj)

    def getEnumerated(self,element):
        return self._inspected_type['getEnumerated'](element)
