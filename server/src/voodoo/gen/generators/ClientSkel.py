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
import sys
import threading

import voodoo.abstraction.abstract_class_generator as acg
import voodoo.gen.protocols.Protocols as _Protocols

#TODO: gestion de hilos (en begin deberian lanzarse en otros hilos)

# This is a Client Skeleton
#
# It is an abstract class (when someone tries to instanciate a subclass of it, it
#   will check if all its methods are implemented, and, if they aren't, an exception
#   is thrown), which has as abtract methods, the methods passed in "methods"

def generate(methods):
    try:
        if isinstance(methods, dict):
            temporal_methods = methods.copy()
            temporal_methods['test_me'] = 'test doc'
            for i in methods:
                temporal_methods['call_begin_'+i] = 'Dynamically generated method'
                temporal_methods['call_is_running_'+i] = 'Dynamically generated method'
                temporal_methods['call_get_result_'+i] = 'Dynamically generated method'
            methods = temporal_methods
        else:
            new_methods = list(methods[:])
            new_methods.append('test_me')
            for i in methods:
                new_methods.append('call_begin_'+i)
                new_methods.append('call_is_running_'+i)
                new_methods.append('call_get_result_'+i)
            methods = new_methods
    except TypeError:
        raise TypeError('methods "%s" must be a dict or a list-able structure' % methods)
        
    #As the ClientSkel is dynamically generated
    #we can't call the call_abstract_constructors
    #function, so we have to call the AbstractClass
    #instance manually :-(
    abstractClass = acg.AbstractClass(methods)

    #
    # The ClientSkel will have (being MN the name of the method):
    #
    # * A dictionary for each method, having the server key (__server_keys_MN)
    #
    # * A dictionary for each method, having the server result (__server_results_MN)
    #
    # * A dictionary with locks for each key of each method (__key_locks_MN)
    # 
    # * A counter for each method, which will be incremented
    #   whenever _get_new_key is called (__key_counter_MN)
    #
    # * A lock for each method (__method_lock_MN)
    #

    # It's important to notice that the local key will be different
    # to the key assigned from the server. It might even be of a
    # different data type.
    #
    class ClientSkel(abstractClass):
        def __init__(self,server):
            abstractClass.__init__(self)
            self._server = server
            self._general_lock = threading.Lock()

        def _get_new_key(self,method_name):
            self._general_lock.acquire()
            if not hasattr(self,'__server_keys_'+method_name):
                setattr(self,'__server_keys_'+method_name,{})
                setattr(self,'__key_counter_'+method_name,0)
                setattr(self,'__method_lock_'+method_name,threading.Lock())
                setattr(self,'__key_locks_'+method_name,{})
            self._general_lock.release()
            
            method_lock = getattr(self,'__method_lock_'+method_name)
            method_lock.acquire()
            try:
                new_key = getattr(self,'__key_counter_'+method_name)+1
                setattr(self,'__key_counter_'+method_name,new_key)
                method_lock_key_dict = getattr(self,'__key_locks_'+method_name)
                method_lock_key_dict[new_key] = threading.Lock()
            finally:
                method_lock.release()
            return new_key
        
        def _get_method_lock(self,method_name):
            return getattr(self,'__method_lock_'+method_name)
        def _get_key_lock(self,method_name,key):
            method_lock = self._get_method_lock(method_name)
            method_lock.acquire()
            try:
                method_lock_key_dict = getattr(self,'__key_locks_'+method_name)
                return method_lock_key_dict[key]
            finally:
                method_lock.release()
        def _get_server_key(self,method_name,key):
            method_lock = self._get_method_lock(method_name)
            method_lock.acquire()
            try:
                server_keys = getattr(self,'__server_keys_'+method_name)
                return server_keys[key]
            finally:
                method_lock.release()
        def _set_server_key(self,method_name,key,server_key):
            method_lock = self._get_method_lock(method_name)
            method_lock.acquire()
            try:
                server_keys = getattr(self,'__server_keys_'+method_name)
                server_keys[key] = server_key
            finally:
                method_lock.release()
        
    def generate_begin_method(METHOD_NAME):
        def begin_method(self,*parameters,**kparameters):
            """ Dynamically generated method. Protocols: Direct. Method name: METHOD_NAME. It starts the call in background """
            new_key = self._get_new_key(METHOD_NAME)

            server_key = getattr(self,'call_begin_'+METHOD_NAME)(*parameters,**kparameters)
            self._set_server_key(METHOD_NAME,new_key,server_key)
            return new_key
        return begin_method

    def generate_is_running_method(METHOD_NAME):
        def is_running_method(self,key,block = False):
            """ Dynamically generated method. Protocols: Direct. Method name: METHOD_NAME. It will return wether the method is still running or not in the server. The key must be a begin_METHOD_NAME returned key. If "block" is set to True, the petition will last during a couple of seconds in server. """
            server_key = self._get_server_key(METHOD_NAME,key)
            return getattr(self,'call_is_running_'+METHOD_NAME)(server_key,block)
        return is_running_method
    
    def generate_end_method(METHOD_NAME):
        def end_method(self,key):
            """ Dynamically generated method. Protocols: Direct. Method name: METHOD_NAME. It will wait until the method is finished, and will return the result. """
            is_running_method = getattr(self,'is_running_'+METHOD_NAME)
            get_result_method = getattr(self,'get_result_'+METHOD_NAME)
            while is_running_method(key,True):
                pass
            return get_result_method(key)
        return end_method
    
    def generate_get_result_and_wait_method(METHOD_NAME):
        def get_result_and_wait_method(self,key):
            server_key = self._get_server_key(METHOD_NAME,key)
            key_lock = self.get_key_lock(METHOD_NAME,key)
            key_lock.acquire()
            try:
                if not hasattr(self,'__result_'+METHOD_NAME+'_'+key):
                    the_result = getattr(self._server,'get_result_'+METHOD_NAME)(server_key)
                    setattr(self,'__result_'+METHOD_NAME+'_'+key,the_result)
            finally:
                key_lock.release()
        return get_result_and_wait_method
        
    def generate_get_result_method(METHOD_NAME):
        def get_result_method(self,key):
            server_key = self._get_server_key(METHOD_NAME,key)
            key_lock = self.get_key_lock(METHOD_NAME,key)
            key_lock.acquire()
            try:
                if hasattr(self,'__result_'+METHOD_NAME+'_'+key):
                    the_result = getattr(self,'__result_'+METHOD_NAME+'_'+key)
                    delattr(self,'__result_'+METHOD_NAME+'_'+key)
                    return the_result
                return getattr(self,'call_get_result_'+METHOD_NAME)(server_key)
            finally:
                key_lock.release()
        return get_result_method

    methods_to_generate = (generate_begin_method, generate_end_method, generate_is_running_method, generate_get_result_and_wait_method, generate_get_result_method)
    
    for method in methods:
        for method_to_generate in methods_to_generate:
            new_method = method_to_generate(method)
            if new_method.__doc__ != None:
                new_method.__doc__ = new_method.__doc__.replace('METHOD_NAME',method)
            method_name = method_to_generate.func_name
            new_method_name = method_name[:method_name.rfind('method')] + method
            new_method.func_name = new_method_name
            setattr(ClientSkel,new_method_name,new_method)

    return ClientSkel

#This function will return a dynamically generated class which will be
#a subclass of a dynamically generated ClientSkell with the methods
#passed in "methods". The subclass will use the "protocol" type of 
#communication to communicate the client with the server
#
#This way, all the code subclassing the returned class will be
#in practice independent from the type of communication. By changing
#the "protocol" value, all the code down will use other kind of 
#communication (such as direct communication, SOAP, XML-RPC, Jabber...)

def factory(protocol, methods):
    if not _Protocols.isProtocols(protocol):
        raise TypeError('protocol "%s" not a valid Protocols value' % protocol)
    if not isinstance(methods,list) and not isinstance(methods,dict):
        raise TypeError('methods "%s" not a dict or list' % methods)
    #If protocol is a valid protocol (ie 'Direct') it will look for the following class:
    # mySystem.calls.Direct.ClientDirect
    moduleName = 'Client'+protocol
    
    #mySystem will be something like 'voodoo.'
    mySystem = __name__[:__name__.find('generators')]
    full_module_name = mySystem+'protocols.'+protocol+'.'+moduleName
    __import__(full_module_name, globals(), locals())
    module = sys.modules[full_module_name]
    return module.generate(methods)

