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
import voodoo.gen.coordinator.Access as Access

name = "Direct"

class DirectNetwork(Access.Network):
    def __init__(self,address):
        """ address is CoordAddress representing the server """
        Access.Network.__init__(self,address)
    def check(self,other):
        return [ i for i in other.networks
            if isinstance(i,DirectNetwork) and self.__both_servers_in_same_instance(i) ]

    def __both_servers_in_same_instance(self,i):
        return (
                self.address.machine_id == i.address.machine_id
                and self.address.instance_id == i.address.instance_id
            )

    def get_protocol(self):
        import voodoo.gen.protocols.Direct.Network as Network
        # self.__module__ will change if someone inherits DirectNetwork
        return Network

