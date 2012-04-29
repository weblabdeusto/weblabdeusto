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

import SimpleXMLRPCServer
import threading
import new
import types
import traceback

import voodoo.log as log
import voodoo.counter as counter

import voodoo.resources_manager as ResourceManager

#TODO: configuration
MAX_TIMEOUT = 0.5

_xmlrpc_server = None
_xmlrpc_server_functions = []
_xmlrpc_server_lock = threading.Lock()

class UtilRequestHandlerClass(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    def log_message(self, format, *args):
        log.log(
                UtilRequestHandlerClass,
                log.level.Info,
                "Request: %s" % (format % args)
            )

class _XMLRPCServerResourceManager(ResourceManager.ResourceManager):
    def dispose_resource(self, resource):
        try:
            resource.cancel()
        except:
            pass
        try:
            resource.join()
        except:
            pass

_resource_manager = _XMLRPCServerResourceManager()

def _generate_skeleton(METHOD_NAME):
    # Skeleton of method to dynamically generate
    def _skeleton(self,*parameters,**kparameters):
        """ Dynamically generated method. Protocol: XMLRPC.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        try:
            return getattr(self._parent,'do_'+METHOD_NAME)(*parameters,**kparameters)
        except Exception as e:
            # TODO: watch out, if server gets a Control + C, the exception is going to propagate
            tb = traceback.format_exc()
            if type(e) == types.InstanceType:
                class_name = str(e.__class__)
            else:
                class_name = type(e).__module__ + '.' + type(e).__name__
            log.log(self,log.level.Info,"Exception : " + class_name + "; " + e.args[0] + "; " + tb)
            raise
    return _skeleton

# TODO: Threading?
class _AvoidTimeoutXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):

    request_queue_size = 50 #TODO: configure this

    def get_request(self):
        sock, addr = SimpleXMLRPCServer.SimpleXMLRPCServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

# Don't use this method directly.
# Use voodoo.gen.generators.ServerSkel.factory(cfg_manager,protocols,methods)
def generate(cfg_manager, methods):
    
    class ServerXMLRPC(threading.Thread):
        def __init__(self,who,port):
            super(ServerXMLRPC,self).__init__()
            self.setName(counter.next_name("ServerXMLRPC"))
            self._register_xmlrpc_server(who,port)

            self._stop_lock = threading.Lock()
            self._stopped   = False
            self._port      = port
            self._who       = who

        def _register_xmlrpc_server(self,who,port):
            _xmlrpc_server_lock.acquire()
            try:
                global _xmlrpc_server
                if _xmlrpc_server == None:
                    _xmlrpc_server = {}
                if not _xmlrpc_server.has_key(port):
                    _xmlrpc_server[port] = _AvoidTimeoutXMLRPCServer((who,port), requestHandler=UtilRequestHandlerClass, allow_none = True)
                    _xmlrpc_server[port].socket.settimeout(MAX_TIMEOUT)
                self.server = _xmlrpc_server[port]

                for i in all_methods:
                    if i in _xmlrpc_server_functions:
                        log.log(ServerXMLRPC,log.level.Warning,'Method "%s" already served by server "%s"' % (i,self))
                    #Register every function from "all_methods"
                    self.server.register_function(new.instancemethod(getattr(self.__class__,i),self,self.__class__), 'Util.%s' % i)
                    _xmlrpc_server_functions.append(i)
    
            finally:
                _xmlrpc_server_lock.release()

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
        func.__doc__ = (func.__doc__ if func.__doc__ is not None else '').replace('METHOD_NAME', method_name)
        if isinstance(all_methods, dict):
            func.__doc__ = (func.__doc__ if func.__doc__ is not None else '').replace('DOCUMENTATION', all_methods[method_name])
        setattr(ServerXMLRPC, method_name, func)

    return ServerXMLRPC
