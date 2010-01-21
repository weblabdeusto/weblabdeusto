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

import socket as _socket

class SocketManagerConstructionException(Exception):
    pass    
class InternetSocketManagerConstructionException(Exception):
    pass
class UnixSocketManagerConstructionException(Exception):
    pass

class SocketManager(object):

    def __init__(self, socket_type=None, address=None, socket=None):
        """Multiple constructors format: every argument must be passed with its name, i.e:
            s = SocketManager(socket_type=socket.AF_INET, hostname='', port=50000))
            s = SocketManager(socket_type=socket.AF_INET, socket=mysocket))
            s = SocketManager(socket_type=socket.AF_UNIX, path=mypath))
            s = SocketManager(socket_type=socket.AF_UNIX, socket=mysocket)"""
        super(SocketManager, self).__init__()
        if socket_type == None:
            raise SocketManagerConstructionException("socket_type argument must have a value")
        self._type = socket_type
        if socket != None:
            self._socket = socket
            self._address = self._socket.getpeername()
        elif address != None:
            self._address = address
            self._socket = None
        else:
            raise SocketManagerConstructionException("You must provide an address or a socket")

    def connect(self):
        self._socket = _socket.socket(self._type, _socket.SOCK_STREAM)
        self._socket.connect(self._address)

    def send(self, message):
        total_sent = 0
        while total_sent < len(message):
            total_sent += self._socket.send(message[total_sent:])

    def receive(self):  
        # Reading the size of the message
        size_str = self._socket.recv(10)
        if not size_str:
            return None
        size = int(size_str) + 1 # \n
        data = ""
        while len(data) != size:
            remaining = size - len(data)
            if remaining > 4096:
                remaining = 4096
            data += self._socket.recv(remaining)
        return size_str+data

    def disconnect(self):
        self._socket.close()
        
class InternetSocketManager(SocketManager):
    
    def __init__(self, hostname=None, port=None, socket=None):
        if socket != None:
            super(InternetSocketManager, self).__init__(socket_type=_socket.AF_INET, socket=socket)
        elif hostname != None and port != None:
            super(InternetSocketManager, self).__init__(socket_type=_socket.AF_INET, address=(hostname, port))
        else:
            raise InternetSocketManagerConstructionException("You must provide a (hostname, port) or a socket")
        
class UnixSocketManager(SocketManager):
    
    def __init__(self, path=None, socket=None):
        if socket != None:
            super(UnixSocketManager, self).__init__(socket_type=_socket.AF_UNIX, socket=socket)
        elif path != None:
            super(UnixSocketManager, self).__init__(socket_type=_socket.AF_UNIX, address=path)
        else:
            raise UnixSocketManagerConstructionException("You must provide a path or a socket")
