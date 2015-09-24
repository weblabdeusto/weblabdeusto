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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import sys
import voodoo.log as log
try:
    import serial
except ImportError:
    SERIAL_AVAILABLE = False
else:
    SERIAL_AVAILABLE = True

def check_serial_available(func):
    def wrapped(self, *args, **kargs):
        if not SERIAL_AVAILABLE:
            msg = "The optional library 'pyserial' is not available. The experiments trying to use the serial port will fail."
            print(msg, file=sys.stderr)
            log.log(self, log.level.Error, msg)
            return
        return func(self, *args, **kargs)
    return wrapped

class SerialPort(object):
    @check_serial_available
    def open_serial_port(self, port_number):
        self.ser = serial.Serial(port_number)

    @check_serial_available
    def send_code(self, code):
        self.ser.write(chr(code))

    @check_serial_available
    def close_serial_port(self):
        self.ser.close()

