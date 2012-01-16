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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import voodoo.gen.protocols.BaseSocket.Messages as Messages

import sys

def _retrieve_class(complete_class_name):
    copy_of_complete_class_name = complete_class_name
    while copy_of_complete_class_name != '' and not sys.modules.has_key(copy_of_complete_class_name):
        copy_of_complete_class_name = copy_of_complete_class_name[:copy_of_complete_class_name.rfind('.')]
    if copy_of_complete_class_name == '':
        return None
    module = sys.modules[copy_of_complete_class_name]
    class_name = complete_class_name[len(copy_of_complete_class_name)+1:]
    if not hasattr(module,class_name):
        return None
    return getattr(module,class_name)


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
    # TODO: The docstring related to the protocol is always BaseSocket
    def _stub(self, *parameters, **kparameters):
        """ Dynamically generated method. Protocol: BaseSocket.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        formatter = Messages.MessageFormatter()
        message_to = formatter.pack_call(METHOD_NAME, *parameters, **kparameters)
        self._server.connect()
        try:
            self._server.send(message_to)
            message_from = self._server.receive()
        finally:
            self._server.disconnect()
        result = formatter.unpack_result(message_from)
        return result.answer()
    return _stub

def _generate_call_begin_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    # TODO: The docstring related to the protocol is always BaseSocket
    def _call_begin_stub(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: BaseSocket.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        pass
    return _call_begin_stub

def _generate_call_is_running_stub(METHOD_NAME):
    # Not used for the moment by ClientSkel
    # TODO: The docstring related to the protocol is always BaseSocket
    def _call_is_running_stub(self,server_key,block):
        """ Dynamically generated method. Protocol: BaseSocket.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        pass
    return _call_is_running_stub

def _generate_call_get_result_stub(METHOD_NAME):
    # Not used for the moment by ClientSkel
    # TODO: The docstring related to the protocol is always BaseSocket
    def _call_get_result_stub(self,server_key):
        """ Dynamically generated method. Protocol: BaseSocket.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        pass
    return _call_get_result_stub

# Tuple with the stub pointers of the stubs to generate
stubs = (
    _generate_stub,
    _generate_call_begin_stub,
    _generate_call_is_running_stub,
    _generate_call_get_result_stub
)           

def generate_base(methods, ClientSocket):
    
    # Adding properly the testing method to check availability
    if isinstance(methods, dict):
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
            setattr(ClientSocket, func_name, func)
        
    return ClientSocket
