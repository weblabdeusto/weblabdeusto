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
import voodoo.gen.exceptions.locator.LocatorExceptions as LocatorExceptions

class ServerTypeHandler(object):
    def __init__(self,server_type_module, methods):
        """ server_type_type is a Enumeration-created type.

        For example: voodoo.gen.protocols.protocols.Protocols
        (not voodoo.gen.protocols.protocols, that's only a module).

        The second parameter, "methods", must be a dictionary like:
        {
            EnumerationMember1Name : 'method_name1',
            EnumerationMember2Name : 'method_name2',
            ...
        }
        """

        for klass in methods:
            if not isinstance(methods[klass], (list, tuple)):
                raise LocatorExceptions.InvalidListOfMethodsException("Invalid format at ServerTypeHandler. Expected tuple or list, found: %s" % methods[klass] )

#        for klass in methods:
#            if not hasattr(server_type_type, klass):
#                raise LocatorExceptions.MoreServersThanExpectedException("Unexpected class %s for module %s" % (klass, server_type_type))

        self._module = server_type_module

        self._methods = methods

    def retrieve_methods(self,server_type):
        if self._methods.has_key(server_type):
            return self._methods[server_type]
        else:
            raise LocatorExceptions.NoSuchServerTypeFoundException(
                    "Server type '%s' not found retrieving methods" % server_type
                )

    @property
    def module(self):
        return self._module

    def isMember(self, obj):
        if isinstance(obj, basestring):
            return hasattr(self._module, obj)

        # TODO: remove the line below and put "return False"
        return hasattr(obj, 'name') and hasattr(self._module, obj.name)

