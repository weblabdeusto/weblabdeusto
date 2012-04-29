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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import voodoo.gen.generators.ClientSkel as ClientSkel
import voodoo.gen.protocols.BaseSocket.ClientBaseSocket as ClientBaseSocket
from voodoo.gen.protocols.BaseSocket.SocketManager import InternetSocketManager

def generate(methods):
    clientSkel = ClientSkel.generate(methods)

    class ClientInternetSocket(clientSkel):
        def __init__(self, hostname, port):
            clientSkel.__init__(self, InternetSocketManager(hostname=hostname, port=port))

    return ClientBaseSocket.generate_base(methods, ClientInternetSocket)
