#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import sys
import cPickle as pickle

try:
    import SOAPpy
except ImportError:
    SOAPPY_AVAILABLE = False
else:
    SOAPPY_AVAILABLE = True

import voodoo.gen.generators.ClientSkel as ClientSkel
import voodoo.gen.exceptions.protocols.ProtocolErrors as ProtocolErrors
import voodoo.log as log

import voodoo.gen.protocols.SOAP.server as ServerSOAP
import voodoo.gen.protocols.SOAP.errors as Exceptions
import voodoo.mapper as mapper

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
    def _stub(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: SOAP.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        try:
            if ServerSOAP.SERIALIZE:
                parameters_instance = (parameters, kparameters)
                if ServerSOAP.SERIALIZE_MAPPING:
                    parameters_instance = mapper.dto_generator(parameters_instance)
                dumped_result = getattr(self._server,METHOD_NAME)(
                        pickle.dumps(parameters_instance)
                    )
                result = pickle.loads(dumped_result)
                if ServerSOAP.SERIALIZE_MAPPING:
                    result = mapper.load_from_dto(result)
                return result
            else:
                return getattr(self._server,METHOD_NAME)(*parameters,**kparameters)
        except SOAPpy.faultType as ft:
            #TODO: if server receives a control + c, client gets it :-o
            class_type = _retrieve_class(ft.faultcode)
            if class_type is not None:
                try:
                    instance = class_type(ft.faultstring)
                except:
                    pass
                else:
                    raise instance
            raise Exceptions.UnknownFaultType(
                    "Unknown fault type: " + str(ft.faultcode) + ": " + str(ft.faultstring) + "; " + str(ft.detail),
                    ft
                )
        except Exception as e:
            raise ProtocolErrors.UnknownRemoteError(
                    "Unknown exception: " + str(e.__class__) + "; " + str(e),
                    e
                )
    return _stub

def _generate_call_begin_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    def _call_begin_stub(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: SOAP.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        return getattr(self._server,'begin_'+METHOD_NAME)(*parameters,**kparameters)
    return _call_begin_stub

def _generate_call_is_running_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    def _call_is_running_stub(self,server_key,block):
        """ Dynamically generated method. Protocol: SOAP.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        return getattr(self._server,'is_running_'+METHOD_NAME)(server_key,block)
    return _call_is_running_stub

def _generate_call_get_result_stub(METHOD_NAME):
    # Not used for the moment but requierd by ClientSkel
    def _call_get_result_stub(self,server_key):
        """ Dynamically generated method. Protocol: SOAP.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        return getattr(self._server,'get_result_'+METHOD_NAME)(server_key)
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

    class ClientSOAP(clientSkel):
        def __init__(self, url, port=80):
            if SOAPPY_AVAILABLE:
                proxy = SOAPpy.SOAPProxy('http://'+url+':'+str(port))
            else:
                proxy = None
                msg = "The optional library 'SOAPpy' is not available. The communications between different servers will not work through SOAP. Since the client is being instanciated, there will probably be uncommon errors."
                print >> sys.stderr, msg
                log.log(self, log.level.Error, msg)

            clientSkel.__init__(self, proxy)

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
            setattr(ClientSOAP, func_name, func)

    return ClientSOAP
