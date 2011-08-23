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

import socket

if hasattr(socket,'AF_UNIX'):
    import voodoo.gen.protocols.BaseSocket.ServerBaseSocket as ServerBaseSocket
    import voodoo.gen.protocols.BaseSocket.SocketManager as SocketManager
    import voodoo.resources_manager as ResourceManager

    import SocketServer

    class _UnixSocketServerResourceManager(ResourceManager.ResourceManager):
        def dispose_resource(self, resource):
            try:
                resource.cancel()
            except:
                pass
            try:
                resource.join()
            except:
                pass            
    _resource_manager = _UnixSocketServerResourceManager()

    class AvoidTimeoutThreadingUnixStreamServer(SocketServer.ThreadingUnixStreamServer):
        
        def get_request(self):
            sock, addr = SocketServer.ThreadingUnixStreamServer.get_request(self)
            sock.settimeout(None)
            return sock, addr

    class SocketHandler(ServerBaseSocket.SocketHandler):
            
        def __init__(self, *args, **kargs):
            self._SocketManager = SocketManager.UnixSocketManager
            ServerBaseSocket.SocketHandler.__init__(self, *args, **kargs)   

    class ServerSocket(ServerBaseSocket.ServerSocket):
        
        def __init__(self, path):
            self._AvoidTimeoutThreadingServer = AvoidTimeoutThreadingUnixStreamServer
            class NewSocketHandler(SocketHandler):
                _functions = {}
            self._SocketHandler = NewSocketHandler
            self._address = path
            super(ServerSocket, self).__init__()
        

    # Don't use this method directly.
    # Use voodoo.gen.generators.ServerSkel.factory(cfg_manager,protocols,methods)
    def generate(cfg_manager, methods):
        
        # This is because the real class must be outside generate() (to let the test access it),
        # and at the same time, we need a unique class for each generate() call.
        class ServerUnixSocketUnique(ServerSocket):
            _all_methods = methods

        return ServerBaseSocket.generate_base(methods, ServerUnixSocketUnique)
