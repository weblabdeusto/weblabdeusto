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

import unittest

import test.util.optional_modules as optional_modules
from weblab.experiment.devices import serial_port

class SerialPortTestCase(optional_modules.OptionalModuleTestCase):
    MODULE    = serial_port
    ATTR_NAME = 'SERIAL_AVAILABLE'

    def test_serial_not_available(self):
        def func():
            serial = serial_port.SerialPort()
            serial.open_serial_port(1)
            serial.send_code(65)
            serial.close_serial_port()

        self._test_func_without_module(func)

def suite():
    return unittest.makeSuite(SerialPortTestCase)

if __name__ == '__main__':
    unittest.main()
