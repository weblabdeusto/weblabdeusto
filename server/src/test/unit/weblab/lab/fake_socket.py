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

import socket as real_socket

OK = "OK"
ERROR = "ERROR"

expected_action = OK

def reset():
    global expected_action
    expected_action = OK

class socket(object):

    def __init__(self, *args, **kargs):
        super(socket, self).__init__()

    def connect(self, (hostname, port)):
        if expected_action == OK:
            pass
        elif expected_action == ERROR:
            raise real_socket.error("")
        else:
            raise RuntimeError("Unknown value for return_value in fake socket.connect()")

    def close(self):
        pass
