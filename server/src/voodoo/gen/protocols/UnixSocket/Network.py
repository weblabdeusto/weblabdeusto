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

import voodoo.gen.coordinator.Access as Access

name = "UnixSocket"

class UnixSocketNetwork(Access.Network):

    def __init__(self, address):
        """ address is CoordAddress representing the server """
        Access.Network.__init__(self, address)

    def check(self, other):
        return [ i for i in other.networks
            if isinstance(i, UnixSocketNetwork) and self.__both_servers_in_same_machine(i) ]

    def __both_servers_in_same_machine(self, i):
        return self.address.machine_id == i.address.machine_id

    def get_protocol(self):
        import voodoo.gen.protocols.UnixSocket.Network as Network
        # self.__module__ will change if someone inherits DirectNetwork
        return Network
