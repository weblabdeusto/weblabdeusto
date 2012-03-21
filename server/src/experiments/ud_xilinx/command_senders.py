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

from voodoo.override import Override
from experiments.ud_xilinx.exc import InvalidDeviceToSendCommandsError
from weblab.experiment.devices.http import HttpDevice
from weblab.experiment.devices.serial_port import SerialPort
from experiments.ud_xilinx import command as UdBoardCommand
import threading


_SerialPort = SerialPort
_HttpDevice = HttpDevice


class UdXilinxCommandSender(object):

    def __init__(self, cfg_manager):
        super(UdXilinxCommandSender, self).__init__()
        self._cfg_manager = cfg_manager

    @staticmethod
    def create(device_name, cfg_manager):
        if device_name == 'HttpDevice':
            return HttpCommandSender(cfg_manager)
        elif device_name == 'SerialPort':
            return SerialPortCommandSender(cfg_manager)
        else:
            raise InvalidDeviceToSendCommandsError(device_name)

    def send_command(self, command):
        raise NotImplementedError("This method must be overriden in a subclass.")


class SerialPortCommandSender(UdXilinxCommandSender):

    def __init__(self, cfg_manager):
        super(SerialPortCommandSender, self).__init__(cfg_manager)
        self._serial_port = _SerialPort()
        self._port_number = self._cfg_manager.get_value('weblab_xilinx_experiment_port_number')
        self._is_fake     = self._cfg_manager.get_value('xilinx_serial_port_is_fake', False)
        self._serial_port_lock = threading.Lock()

    @Override(UdXilinxCommandSender)
    def send_command(self, command):
        if self._is_fake:
            print "Sending command...", command
            return
        cmd = UdBoardCommand.UdBoardCommand(command)
        codes = cmd.get_codes()
        self._serial_port_lock.acquire()
        try:
            self._serial_port.open_serial_port(self._port_number)
            for i in codes:
                self._serial_port.send_code(i)
            self._serial_port.close_serial_port()
        finally:
            self._serial_port_lock.release()


class HttpCommandSender(UdXilinxCommandSender):

    def __init__(self, cfg_manager):
        super(HttpCommandSender, self).__init__(cfg_manager)
        ip = self._cfg_manager.get_value('xilinx_http_device_ip')
        port = self._cfg_manager.get_value('xilinx_http_device_port')
        app = self._cfg_manager.get_value('xilinx_http_device_app')
        self._http_device = _HttpDevice(ip, port, app)

    @Override(UdXilinxCommandSender)
    def send_command(self, command):
        self._http_device.send_message(command)
