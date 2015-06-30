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

import socket

class Socket(object):

    def __init__(self, hostname, port):
        super(Socket, self).__init__()
        self._hostname = hostname
        self._port     = port
        self._socket = None

    def connect(self):
        self._socket = self._create_socket()
        self._socket.connect((self._hostname, self._port))

    def send(self, message):
        self._socket.send(message)

    def receive(self):
        return self._socket.recv(4096)

    def close(self):
        self._socket.close()

    def _create_socket(self):
        return socket.socket(socket.AF_INET, socket.STREAM)