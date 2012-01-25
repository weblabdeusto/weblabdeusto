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

if hasattr(socket, 'AF_UNIX'):

    import voodoo.gen.generators.ClientSkel as ClientSkel
    import voodoo.gen.protocols.BaseSocket.ClientBaseSocket as ClientBaseSocket
    from voodoo.gen.protocols.BaseSocket.SocketManager import UnixSocketManager

    def generate(methods):
        clientSkel = ClientSkel.generate(methods)

        class ClientUnixSocket(clientSkel):
            def __init__(self, path):
                clientSkel.__init__(self, UnixSocketManager(path=path))

        return ClientBaseSocket.generate_base(methods, ClientUnixSocket)
