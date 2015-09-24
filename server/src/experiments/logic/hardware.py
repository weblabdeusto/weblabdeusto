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

import os
from abc import ABCMeta, abstractmethod
from voodoo.threaded import threaded
from socket import AF_INET, SOCK_STREAM, socket

import experiments.ud_xilinx.exc as UdXilinxExperimentErrors
from experiments.ud_xilinx.command_senders import UdXilinxCommandSender
from weblab.experiment.devices.xilinx.programmers.programmers import XilinxProgrammer


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
            s.send(TEMPLATE % {'SIZE': length, 'MSG': msg})
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
    def __init__(self, cfg_manager):
        self._cfg_manager = cfg_manager
        self._board_type = self._cfg_manager.get_value('xilinx_board_type')
        self._programmer_type = self._cfg_manager.get_value('xilinx_programmer_type')

        self._programmer = self._load_programmer(self._programmer_type, self._board_type)
        self._command_sender = self._load_command_sender()

    def _load_programmer(self, programmer_type, board_type):
        return XilinxProgrammer.create(programmer_type, self._cfg_manager, board_type)

    def _load_command_sender(self):
        device_name = self._cfg_manager.get_value('xilinx_device_to_send_commands')
        return UdXilinxCommandSender.create(device_name, self._cfg_manager)

    def initialize(self):
        if self._board_type == 'PLD':
            file_name = 'turnon.jed'
        else:  # FPGA
            file_name = 'turnon.bit'
        full_file_name = os.path.join(os.path.dirname(__file__), file_name)
        self._programmer.program(full_file_name)

    def send_message(self):
        pass  # Not implemented

    def turn_on(self):
        self._command_sender.send_command("ChangeSwitch on 0")
        self._command_sender.send_command("ChangeSwitch on 0")

    def turn_off(self):
        self._command_sender.send_command("ChangeSwitch on 0")
        self._command_sender.send_command("ChangeSwitch on 9")

    def clear(self):
        self._command_sender.send_command("CleanInputs")
