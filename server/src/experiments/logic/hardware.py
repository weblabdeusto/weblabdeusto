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

from abc import ABCMeta, abstractmethod
from voodoo.threaded import threaded
from socket import AF_INET, SOCK_STREAM, socket

class HardwareInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def send_message(self, msg):
        pass

    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

    @abstractmethod
    def clear(self):
        pass

class HardwareInterfaceCollector(HardwareInterface):
    def __init__(self, interfaces):
        self.interfaces = interfaces

    def initialize(self):
        for interface in self.interfaces:
            interface.initialize()

    def send_message(self, msg):
        for interface in self.interfaces:
            interface.send_message(msg)
        
    def turn_on(self):
        for interface in self.interfaces:
            interface.turn_on()

    def turn_off(self):
        for interface in self.interfaces:
            interface.turn_off()

    def clear(self):
        for interface in self.interfaces:
            interface.clear()

class ConsoleInterface(HardwareInterface):
    def send_message(self, msg):
        print "ConsoleInterface::Sent: ", msg

    def initialize(self):
        print "ConsoleInterface::initialize"

    def turn_on(self):
        print "ConsoleInterface::turn on"
    
    def turn_off(self):
        print "ConsoleInterface::turn on"

    def clear(self):
        print "ConsoleInterface::clear"

class PicInterface(HardwareInterface):
    
    def __init__(self, ip):
        self.ip = ip
        self.last_message = ""

    def initialize(self):
        pass

    @threaded()
    def _send(self, message):
        self.last_message = message.split(';')[0]
        TEMPLATE = "POST / HTTP/1.1\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %(SIZE)s\r\n\r\n%(MSG)s"
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((self.ip, 80))
            msg = "lcd=%s" % message
            length = len(msg)
            s.send(TEMPLATE % {'SIZE' : length, 'MSG' : msg})
            s.close()
        except Exception:
            import traceback
            traceback.print_exc()
            pass

    def send_message(self, message):
        self._send(message + ";0")

    def turn_on(self):
        self._send("%s;1" % self.last_message)

    def turn_off(self):
        self._send("%s;0" % self.last_message)

    def clear(self):
        self._send(";0")

class XilinxInterface(HardwareInterface):
    def __init__(self, impact_file, command_sender):
        pass

    def initialize(self):
        pass

    def send_message(self):
        pass

    def turn_on(self):
        pass

    def turn_off(self):
        pass

    def clear(self):
        pass

