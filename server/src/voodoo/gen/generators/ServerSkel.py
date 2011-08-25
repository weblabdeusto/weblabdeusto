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
from abc import ABCMeta, abstractmethod

import voodoo.gen.generators.Args as Args
import voodoo.gen.protocols.protocols as _Protocols

def _generate_abstract_class(methods):
    methods_code = ""
    for method in methods:
        methods_code += """    
    @abstractmethod
    def %s(self):
        pass
    """ % method

    class_name = 'AbstractServerClass'
    # Passing local variables to avoid pylint warnings
    current_locals = {'ABCMeta' : ABCMeta, 'abstractmethod' : abstractmethod}
    exec(("""class %s(object):
    __metaclass__ = ABCMeta
    """ % class_name) + methods_code, globals(), current_locals)
    return current_locals[class_name]

def _generate_server_skel(methods,servers):
    """ _generate_server_skel(methods, servers) -> class

    If methods has a list like ['method1','method2'], and servers a dictionary like
    {'Direct':(server with the methods),'SOAP':(server with the methods using SOAP)},
    the result will be an abstract class that will require "do_method1" and "do_method2",
    and whenever someone calls "method1" in any of the servers, the "do_method1" method
    will be called.
    """
    if isinstance(methods,dict):
        temporal_methods = {}
        for i in methods:
            temporal_methods['do_'+i] = 'Definition of the method'
    elif isinstance(methods,list) or isinstance(methods,tuple):
        temporal_methods = []
        for i in methods:
            temporal_methods.append('do_'+i)
    else:
        raise TypeError('methods "%s" should be a list, tuple or a dict' % methods)
    methods = temporal_methods
    
    AbstractServerClass = _generate_abstract_class(methods)
    class ServerSkel(AbstractServerClass):
        def __init__(self,**kargs):
            super(ServerSkel, self).__init__()
            self._servers = {}
            
            for i in servers:
                if kargs.has_key(i):
                    args = kargs[i]
                    # Three things can happen:
                    #
                    # a) args has this format: (arg1, arg2, arg3)
                    #     whatever(*args)
                    # b) args has this format: { name1 : arg1, name2 : arg2, name3 : arg3 }
                    #     whatever(**kargs)
                    # c) args is an instance of voodoo.gen.generators.Args.Args
                    #     given arg Args(*args,**kargs), we have to do:
                    #     *arg.args,**arg.kargs
                    #
                    if isinstance(args,Args.Args):
                        self._servers[i] = servers[i](*args.args,**args.kargs)
                    elif isinstance(args,tuple) or isinstance(args,list):
                        self._servers[i] = servers[i](*args)
                    elif isinstance(args,dict):
                        self._servers[i] = servers[i](**args)
                    else:
                        raise TypeError('Invalid argument "%s" for "%s". It should be a list, tuple, dict, or Args' % (args,i))
                        
                else:
                    self._servers[i] = servers[i]()

                # We provide the parent as reference
                self._servers[i].register_parent(self)
        def start(self,daemon = True):
            for i in self._servers:
                self._servers[i].start(daemon)

        def stop(self):
            for i in self._servers:
                self._servers[i].stop()

        def _get_new_key(self,method_name):
            pass
    class ServerSkelWithTest(ServerSkel):
        def __init__(self,**kargs):
            ServerSkel.__init__(self,**kargs)
        def do_test_me(self,arg):
            return arg
    return ServerSkelWithTest
        
#This function will return a dynamically generated class which will be
#a subclass of a dynamically generated ServerSkell with the methods
#passed in "methods". TODO: check this doc
#
#This way, all the code subclassing the returned class will be
#in practice independent from the type of communication. By changing
#the "protocols" value, all the code down will use other kind of 
#communication (such as direct communication, SOAP, XML-RPC, Jabber...)

def factory(cfg_manager, protocols, methods):
    if not _Protocols.isProtocols(protocols): #Maybe it is just one protocol
        try:
            protocols[0]
        except TypeError:
            raise TypeError('protocols "%s" must be either a non-empty sequence or a Protocols' % protocols)
        except IndexError:
            raise TypeError('protocols "%s" must be either a non-empty sequence or a Protocols' % protocols)
        
        for i in protocols:
            if not _Protocols.isProtocols(i):
                raise TypeError('protocol "%s" inside protocols "%s" not a valid Protocols value' % (i,protocols))
        
    if not isinstance(methods,list) and not isinstance(methods,dict) and not isinstance(methods,tuple):
        raise TypeError('methods "%s" must be a dict, tuple or list' % methods)

    def build_server(cfg_manager, protocol):
        #If protocols is a valid protocol (ie 'Direct') it will look for the following class:
        # mySystem.calls.Direct.ServerDirect
        moduleName = 'Server' + protocol
        
        #mySystem will be something like 'voodoo.gen.'
        mySystem = __name__[:__name__.find('generators')]
        full_module_name = mySystem+'protocols.'+protocol+'.'+moduleName
        mod = __import__(full_module_name, globals(), locals(), [ moduleName ])
        return mod.generate(cfg_manager, methods) 

    # "servers" will be a dictionary with the name of the callback as key
    # and a class which uses this protocol to offer the parameters asked
    # in "methods". The value is a class (not an instance)
    servers = {}

    # If it is only one protocol
    if _Protocols.isProtocols(protocols):
        servers[protocols] = build_server(cfg_manager, protocols)
    # If there is a sequence of protocols
    else:
        for i in protocols:
            servers[i] = build_server(cfg_manager, i)

    return _generate_server_skel(methods, servers)

