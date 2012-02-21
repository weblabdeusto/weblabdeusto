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
import re

import voodoo.gen.exceptions.coordinator.CoordinatorExceptions as CoordExceptions

class CoordAddress(object):
    FORMAT = '%(server)s:%(instance)s@%(machine)s'
    REGEX_FORMAT = '^' + FORMAT % {
        'server' : '(.*)',
        'instance' : '(.*)',
        'machine' : '(.*)'
    } + '$'

    def __init__(self,machine_id,instance_id='',server_id=''):
        """ CoordAddress(machine_id,instance_id,server_id) -> CoordAddress

        CoordAddress is the relative address for a server in the CoordinationMap.
        Fields:
            * machine_id
            * instance_id
            * server_id
            * address (an address converted to string
                with CoordAddress.FORMAT format)

        Just in the same way networks ending are represented ending with 0s,
        the CoordAddresses with server field empty are the address for an
        instance, and the CoordAddresses with server and instances fields
        empty are the addresses for machines.
        """
        if not type(machine_id) in (str,unicode) or machine_id == '':
            raise CoordExceptions.CoordInvalidAddressParams( "%s: not a valid machine_id" % machine_id)
        if not type(instance_id) in (str,unicode):
            raise CoordExceptions.CoordInvalidAddressParams( "%s: not a valid instance_id" % instance_id)
        if not type(server_id) in (str,unicode):
            raise CoordExceptions.CoordInvalidAddressParams( "%s: not a valid server_id" % server_id)
        if instance_id == '' and server_id != '':
            raise CoordExceptions.CoordInvalidAddressParams( "%s, %s: not valid parameters" % (instance_id, server_id))

        self.machine_id = machine_id
        self.instance_id = instance_id
        self.server_id = server_id

        self._reload_address()

    def _reload_address(self):
        self._address = CoordAddress.FORMAT % {
                'server'    : self.server_id,
                'instance'  : self.instance_id,
                'machine'   : self.machine_id
            }

    @property
    def address(self):
        return self._address

    # is_* methods
    def is_server(self):
        return self.server_id != ''

    def is_instance(self):
        return self.server_id == '' and self.instance_id != ''

    def is_machine(self):
        return self.server_id == '' and self.instance_id == ''

    # get_* methods
    def get_instance_address(self):
        if not self.is_server():
            raise CoordExceptions.CoordInvalidLevelAddress(
                        '%s: not a server_address' % self
                    )
        new_addr = self.copy()
        new_addr.server_id = ''
        new_addr._reload_address()
        return new_addr

    def get_machine_address(self):
        if not self.is_server() and not self.is_instance():
            raise CoordExceptions.CoordInvalidLevelAddress(
                        '%s: not a server or instance address' % self
                    )
        new_addr = self.copy()
        new_addr.server_id = new_addr.instance_id = ''
        new_addr._reload_address()
        return new_addr

    # deep copy method

    def copy(self):
        return CoordAddress(
                self.machine_id,
                self.instance_id,
                self.server_id
            )

    # factory in order to create new CoordAddresses

    @staticmethod
    def translate_address(address):
        """ translate_address(address) -> CoordAddress

        Given a Coordinator Address in CoordAddress.FORMAT format,
        translate_address will provide the corresponding CoordAddress
        """
        try:
            m = re.match(CoordAddress.REGEX_FORMAT,address)
        except TypeError:
            raise CoordExceptions.CoordInvalidAddressName(
                "%(address)s is not a valid address. Format: %(format)s" % {
                "address" : address,
                "format"  : CoordAddress.FORMAT
            }
            )
        if m is None:
            raise CoordExceptions.CoordInvalidAddressName(
                    '%(address)s is not a valid address. Format: %(format)s' % {
                        'address' : address,
                        'format'  : CoordAddress.FORMAT
                    })
        else:
            server,instance,machine = m.groups()
            return CoordAddress(machine,instance,server)

    # Auxiliar methods

    def __cmp__(self,other):
        if other is None:
            return cmp(self.address,None)
        else:
            if isinstance(other,CoordAddress):
                return cmp(self.address,other.address)
            else:
                return cmp(self.address,None)

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '%(name)s <%(address)s>' % {
            'name'      : self.__class__.__name__,
            'address'   : self.address
        }

    def __repr__(self):
        return 'CoordAddress(%r, %r, %r)' % (
            self.machine_id, self.instance_id, self.server_id )

    def __hash__(self):
        return hash(self.address) + 1

