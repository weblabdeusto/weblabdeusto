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

import voodoo.mapper as mapper
import voodoo.log as log
import pickle

_SERVER_PREFIX = '__server__'
DUPLICATE=False

def _generate_skeleton(METHOD_NAME):
    # Skeleton of method to dynamically generate
    def _skeleton(self, *parameters, **kparameters):
        """ Dynamically generated method. Protocol: Direct.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        if DUPLICATE:
            dumped_parameters_instance = parameters[0]
            parameters_instance = pickle.loads(dumped_parameters_instance)
            real_parameters = mapper.load_from_dto(parameters_instance)
            parameters, kparameters = real_parameters
        return getattr(self._parent, 'do_'+METHOD_NAME)(*parameters, **kparameters)
    return _skeleton

# Don't use this method directly.
# Use voodoo.gen.generators.ServerSkel.factory(cfg_manager,protocols,methods)
def generate(cfg_manager, methods):

    class ServerDirect(object):

        def __init__(self, full_address):
            self._full_address = full_address

        def register_parent(self,parent):
            self._parent = parent
            # We should also register the server in the ServerRegistry
            import voodoo.gen.registry.server_registry as ServerRegistry
            import voodoo.gen.exceptions.registry.RegistryExceptions as RegistryExceptions
            registry = ServerRegistry.get_instance()
            try:
                registry.register_server(_SERVER_PREFIX + self._full_address, self._parent)
            except RegistryExceptions.AddressAlreadyRegisteredException as aar:
                log.log(
                        ServerDirect,
                        log.level.Warning,
                        "Exception registering parent server: AddressAlreadyRegistered: %s" % aar
                    )
                registry.reregister_server(_SERVER_PREFIX + self._full_address,self._parent)

        def start(self, daemon = True):
            pass #No need
        def stop(self):
            pass #No need

    # Adding properly the testing method to check availability
    if isinstance(methods,dict):
        all_methods = methods.copy()
        all_methods['test_me'] = 'test documentation'
    else:
        all_methods = list(methods[:])
        all_methods.append('test_me')

    # Generating skeletons dinamically
    for method_name in all_methods:
        func = _generate_skeleton(method_name)
        func.func_name = method_name
        func.__doc__ = (func.__doc__ if func.__doc__ is not None else '').replace('METHOD_NAME', method_name)
        if isinstance(all_methods, dict):
            func.__doc__ = (func.__doc__ if func.__doc__ is not None else '').replace('DOCUMENTATION', all_methods[method_name])
        setattr(ServerDirect, method_name, func)

    return ServerDirect
