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

from abc import ABCMeta, abstractmethod

import voodoo.gen.exceptions.coordinator.AccessExceptions as AccessExceptions

from voodoo.override import Override
import re

class Address(object):

    __metaclass__ = ABCMeta

    @property
    def address(self):
        return self._get_address()

    @abstractmethod
    def _get_address(self):
        """ _get_address(self) -> str

        It returns the serialized address.
        """

    @abstractmethod
    def create_client(self, methods):
        """ create_client(self, methods) -> client

        Given the list (or dictionary) of methods, this method
        will return an instance with the "methods" methods, and
        each time a method is invoked, the server with this
        address executes the method.
        """

    @abstractmethod
    def get_protocol(self):
        """ get_protocol(self) -> Protocols

        It will return the Protocols
        """

    @abstractmethod
    def __cmp__(self):
        """"""

    @abstractmethod
    def __eq__(self, other):
        """"""

    def __ne__(self, other):
        return not self.__eq__(other)

class IpBasedAddress(Address):
    """
        Abstract class, useful for Ip based protocols.

        create_client will be implemented by the Address that
        inherits this class
    """

    FORMAT = "%(address)s:%(port)s@%(net_name)s"
    REGEX_FORMAT = FORMAT % {
        'address'   : '(.+)', #It can be whatever.com, for example
        'net_name'  : '(.+)', #Any name
        'port'      : '([0-9]{1,5})' #Port
    }

    def __init__(self,address):
        Address.__init__(self)
        o = re.match(self.REGEX_FORMAT,address)
        if o is None:
            raise AccessExceptions.AccessInvalidIpBasedFormat(
                'Invalid IP format: %s. Current Format: %s'
                % ( address, self.FORMAT)
            )
        else:
            self._parse(o.groups())

    def _parse(self, groups):
        self._ip_address, self._port, self._net_name = groups
        self._port = int(self.port)
        if self._port > 65535:
            raise AccessExceptions.AccessInvalidPort(
                    'Invalid port: %s' % self._port
                )
        self._address = self._ip_address + ':' + str(self._port)

    @Override(Address)
    def _get_address(self):
        return self._address

    def _compare(self,other):
        if not isinstance(other,Address):
            return 1

        cmp_ip_address = cmp(self.ip_address,other.ip_address)
        if cmp_ip_address != 0:
            return cmp_ip_address

        cmp_net_name = cmp(self.net_name,other.net_name)
        if cmp_net_name != 0:
            return cmp_net_name

        cmp_port = cmp(self.port,other.port)
        if cmp_port != 0:
            return cmp_port

        return 0

    @Override(Address)
    def __cmp__(self,other):
        return self._compare(self, other)

    @Override(Address)
    def __eq__(self, other):
        return self.__cmp__(other) == 0

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def net_name(self):
        return self._net_name

    @property
    def port(self):
        return self._port


