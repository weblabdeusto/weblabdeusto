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

import voodoo.gen.generators.ClientSkel as ClientSkel
import voodoo.mapper as mapper
import ServerDirect
import pickle

# Stubs of client methods to dynamically generate
# All of them must have the same name format:
#
# _prefix_stub
#
# Where prefix can be:
#    "":                        The method does what it must do (its action)
#    "call_begin"               Designed for asynchronous communication (not used for the moment)
#    "call_is_running"      Designed for asynchronous communication (not used for the moment)
#    "call_get_result"      Designed for asynchronous communication (not used for the moment)

def _generate_stub(METHOD_NAME):
    def _stub(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: Direct.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        if ServerDirect.DUPLICATE:
            parameters_instance = (parameters, kparameters)
            real_parameters = mapper.dto_generator(parameters_instance)
            dumped_real_parameters = pickle.dumps(real_parameters)
            return getattr(self._server._servers['Direct'],METHOD_NAME)(
                    dumped_real_parameters
                )
        else:
            return getattr(self._server._servers['Direct'],METHOD_NAME)(*parameters,**kparameters)
    return _stub

def _generate_call_begin_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    def _call_begin_stub(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: Direct.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        return getattr(self._server._servers['Direct'],'begin_'+METHOD_NAME)(*parameters,**kparameters)
    return _call_begin_stub

def _generate_call_is_running_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    def _call_is_running_stub(self,server_key,block):
        """ Dynamically generated method. Protocol: Direct.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        return getattr(self._server._servers['Direct'],'is_running_'+METHOD_NAME)(server_key,block)
    return _call_is_running_stub

def _generate_call_get_result_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    def _call_get_result_stub(self,server_key):
        """ Dynamically generated method. Protocol: Direct.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        return getattr(self._server._servers['Direct'],'get_result_'+METHOD_NAME)(server_key)
    return _call_get_result_stub

# Tuple with the stub pointers of the stubs to generate
stubs = (
    _generate_stub,
    _generate_call_begin_stub,
    _generate_call_is_running_stub,
    _generate_call_get_result_stub
)

def generate(methods):
    clientSkel = ClientSkel.generate(methods)
    
    class ClientDirect(clientSkel):
        def __init__(self,server):
            clientSkel.__init__(self,server)
    
    # Adding properly the testing method to check availability
    if isinstance(methods,dict):
        all_methods = methods.keys()
    else:
        all_methods = list(methods[:])
    all_methods.append('test_me')
    
    # Generating stubs dinamically
    for method_name in all_methods:
        
        # Each method can have many stubs (with different prefixes)
        for stub in stubs:
            func = stub(method_name)
            # Setting docstring
            func.__doc__ = (func.__doc__ if func.__doc__ is not None else '').replace('METHOD_NAME', method_name)
            if isinstance(all_methods, dict):
                func.__doc__ = (func.__doc__ if func.__doc__ is not None else '').replace('DOCUMENTATION', all_methods[method_name])
            # Taking "prefix_" from "_prefix_stub" 
            stub_prefix = stub.func_name[len('_generate_'):]
            stub_prefix = stub_prefix[:stub_prefix.rfind('stub')]
            func_name = stub_prefix + method_name
            func.func_name = func_name
            setattr(ClientDirect, func_name, func)
    
    return ClientDirect
