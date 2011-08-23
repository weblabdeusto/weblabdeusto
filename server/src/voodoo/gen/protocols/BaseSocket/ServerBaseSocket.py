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

"""
This is not a real protocol, it is only a base to create
InternetSocket and UnixSocket reusing all their common source code.
"""

import threading
import SocketServer

import voodoo.gen.protocols.BaseSocket.Messages as Messages

import voodoo.log as log
import voodoo.counter as counter
import voodoo.resources_manager as ResourceManager

# TODO: configuration
MAX_TIMEOUT = 0.5

class _BaseSocketServerResourceManager(ResourceManager.ResourceManager):
    def dispose_resource(self, resource):
        try:
            resource.cancel()
        except:
            pass
        try:
            resource.join()
        except:
            pass
_resource_manager = _BaseSocketServerResourceManager()

def _generate_skeleton(METHOD_NAME):
    # Skeleton of server method to dynamically generate
    # TODO: The docstring related to the protocol is always BaseSocket
    def _skeleton(self, *parameters, **kparameters): 
        """ Dynamically generated method. Protocol: BaseSocket.
             Method name: METHOD_NAME. Documentation: DOCUMENTATION """
        try:
            return getattr(self._parent, "do_"+METHOD_NAME)(*parameters, **kparameters)
        except Exception:
            # TODO: watch out, if server gets a Control + C, the exception is going to propagate
            log.log_exc(self, log.LogLevel.Info)
            raise
    return _skeleton
        
# The reason of such a strange way is the use of SocketServer.ThreadingTCPServer
class SocketHandler(SocketServer.BaseRequestHandler):

    _functions = {}

    def __init__(self, *args, **kargs):
        SocketServer.BaseRequestHandler.__init__(self, *args, **kargs)

    @classmethod
    def register_function(klz, func):
        klz._functions[func.__name__] = func

    def handle(self):                  
        socket_manager = self._SocketManager(socket=self.request)
        while True:
            message_from = socket_manager.receive()
            if not message_from:
                break
            formatter = Messages.MessageFormatter()
            func = formatter.unpack_call(message_from)
            # Calling the requested function
            if self._functions.has_key("do_"+func.name):
                try:
                    # 1. Called function is registered and works fine
                    result = self._functions["do_"+func.name](*func.args,**func.kargs)
                    function_result = Messages.FunctionResultOK(result)
                except Exception as ex:
                    # 2. Called function is registered but raises an exception
                    function_result = Messages.FunctionResultError(ex)
            else:
                # 3. Called function is not registered
                function_result = Messages.FunctionResultNotFound()
            message_to = formatter.pack_result(function_result)
            socket_manager.send(message_to)     
        socket_manager.disconnect()


class ServerSocket(threading.Thread):

    def __init__(self):         
        super(ServerSocket, self).__init__()
        self.setName(counter.next_name("VoodooServerSocket"))
        self._stop_lock = threading.Lock()
        self._stopped = False
        self._handler = self._SocketHandler
        self._server = self._AvoidTimeoutThreadingServer(self._address, self._handler)
        self._server.socket.settimeout(MAX_TIMEOUT)

    def register_parent(self, parent):
        self._parent = parent           
        for method_name in list(self._all_methods) + ['test_me']:
            self._handler.register_function(getattr(self._parent, "do_"+method_name))

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
                self._server.handle_request()
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
        

def generate_base(methods, ServerSocket):
    
    # Adding properly the testing method to check availability
    if isinstance(methods, dict):
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
        setattr(ServerSocket, method_name, func)

    return ServerSocket
