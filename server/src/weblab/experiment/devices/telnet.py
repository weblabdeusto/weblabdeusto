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
from __future__ import print_function, unicode_literals

import telnetlib

class TelnetDevice(object):

    def __init__(self, hostname, port=23, encoding='utf-8'):
        super(TelnetDevice,self).__init__()
        self.hostname = hostname
        self.port     = port
        self.encoding = encoding
        self._telnet_device = self._create_telnet()
        self._output = ""

    def write(self, buffer):
        output = self._telnet_device.write(buffer.encode(self.encoding))
        if output is not None:
            self._output += output

    def read(self):
        response = self._output
        self._output = ""
        return response

    def _create_telnet(self):
        return telnetlib.Telnet(self.hostname, self.port)