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

try:
    import SOAPpy
except ImportError:
    SOAPPY_AVAILABLE = False
else:
    SOAPPY_AVAILABLE = True

import threading
import new
import time
import sys
import types
import traceback
import cPickle as pickle

import voodoo.log as log
import voodoo.mapper as mapper
import voodoo.counter as counter

import voodoo.ResourceManager as ResourceManager

#TODO: configuration
MAX_TIMEOUT = 0.5

# 
# It's almost sure that we'll have to set SERIALIZE=True, due to limitations of SOAPpy: 
# it can serialize instances (old-style instances), but it can't serialize objects (which
# is the only thing that there is in Python 3, and is what we use in WebLab for all our
# classes).
# 
SERIALIZE = True
SERIALIZE_MAPPING = False

_soap_server = None
_soap_server_functions = {}
_soap_server_lock = threading.Lock()

class _SOAPServerResourceManager(ResourceManager.ResourceManager):
    def dispose_resource(self, resource):
        try:
            resource.cancel()
        except:
            pass
        try:
            resource.join()
        except:
            pass

_resource_manager = _SOAPServerResourceManager()

# Skeleton of method to dynamically generate
def _generate_skeleton(METHOD_NAME):
    def _skeleton(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: SOAP.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        try:
            if SERIALIZE:
                parameters_instance = pickle.loads(parameters[0])
                if SERIALIZE_MAPPING:
                    parameters_instance = mapper.load_from_dto(parameters_instance)
                params, kparams = parameters_instance
                result = getattr(self._parent,'do_'+METHOD_NAME)(
                            *params,
                            **kparams
                        )
                if SERIALIZE_MAPPING:
                    result = mapper.dto_generator(result)
                dumped_result = pickle.dumps(result)
                return dumped_result
            else:
                return getattr(self._parent,'do_'+METHOD_NAME)(*parameters,**kparameters)
        except Exception,e:
            # TODO: watch out, if server gets a Control + C, the exception is going to propagate
            tb = traceback.format_exc()
            if type(e) == types.InstanceType:
                class_name = str(e.__class__)
            else:
                class_name = type(e).__module__ + '.' + type(e).__name__
            log.log(self,log.LogLevel.Info,"Exception : " + class_name + "; " + e.args[0] + "; " + tb)
            raise SOAPpy.faultType(
                    faultcode=class_name,
                    faultstring=e.args[0],
                    detail=tb
                )
    return _skeleton

if SOAPPY_AVAILABLE:
    class _AvoidTimeoutSOAPServer(SOAPpy.ThreadingSOAPServer):

        request_queue_size  = 50 #TODO: configure this
        allow_reuse_address = True

        def get_request(self):
            sock, addr = SOAPpy.ThreadingSOAPServer.get_request(self)
            sock.settimeout(None)
            return sock, addr

# Don't use this method directly.
# Use voodoo.gen.generators.ServerSkel.factory(cfg_manager, protocols,methods)
def generate(cfg_manager, methods):
    
    class ServerSOAP(threading.Thread):
        def __init__(self,who,port):
            super(ServerSOAP,self).__init__()
            self.setName(counter.next_name("ServerSOAP"))
            self._register_soap_server(who,port)

            self._stop_lock = threading.Lock()
            self._stopped   = False
            self._port      = port
            self._who       = who

        def _register_soap_server(self,who,port):
            if SOAPPY_AVAILABLE:
                _soap_server_lock.acquire()
                try:
                    global _soap_server
                    if _soap_server == None:
                        _soap_server = {}
                    if not _soap_server.has_key(port):
                        _soap_server[port] = _AvoidTimeoutSOAPServer((who,port))
                        _soap_server[port].config.dumpFaultInfo = 0
                        _soap_server[port].socket.settimeout(MAX_TIMEOUT)
                    self.server = _soap_server[port]

                    if port not in _soap_server_functions:
                        _soap_server_functions[port] = []

                    for method_name in all_methods:
                        if method_name in _soap_server_functions[port]:
                            log.log(ServerSOAP,log.LogLevel.Warning,'Method "%s" already served by server "%s" on port %s' % (method_name,self, port))
                        #Register every function from "all_methods"
                        self.server.registerFunction(new.instancemethod(getattr(self.__class__, method_name),self,self.__class__))
                        _soap_server_functions[port].append(method_name)
        
                finally:
                    _soap_server_lock.release()
            else:
                msg = "The optional library 'SOAPpy' is not available. The communications between different servers will not work through SOAP."
                print >> sys.stderr, msg
                log.log(self, log.LogLevel.Error, msg)
                class FakeServer(object):
                    def handle_request(self):
                        time.sleep(MAX_TIMEOUT)
                self.server = FakeServer()

        def register_parent(self,parent):
            self._parent = parent
            
        def _get_stopped(self):
            self._stop_lock.acquire()
            try:
                return self._stopped
            finally:
                self._stop_lock.release()

        def start(self,daemon = True):
            self.setDaemon(daemon)
            threading.Thread.start(self)
            _resource_manager.add_resource(self)

        def run(self):
            try:
                while not self._get_stopped():
                    self.server.handle_request()
            finally:
                _resource_manager.remove_resource(self)

        def cancel(self):
            self.stop()

        def stop(self):
            self._stop_lock.acquire()
            try:
                self._stopped = True
            finally:
                self._stop_lock.release()
            self.join()

    # Adding properly the testing method to check availability
    if isinstance(methods,dict):
        all_methods = methods.copy()
        all_methods['test_me'] = 'test doc'
    else:
        all_methods = list(methods[:])
        all_methods.append('test_me')

    # Generating skeletons dinamically
    for method_name in all_methods:
        func = _generate_skeleton(method_name)
        func.func_name = method_name
        func.__doc__ = func.__doc__.replace('METHOD_NAME', method_name)
        if isinstance(all_methods, dict):
            func.__doc__ = func.__doc__.replace('DOCUMENTATION', all_methods[method_name])
        setattr(ServerSOAP, method_name, func)

    return ServerSOAP
