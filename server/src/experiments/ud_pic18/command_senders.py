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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

from voodoo.override import Override
from weblab.experiment.devices.http import HttpDevice
from weblab.experiment.devices.serial_port import SerialPort

_SerialPort = SerialPort
_HttpDevice = HttpDevice


class UdXilinxCommandSender(object):
    
    def __init__(self, cfg_manager):
        super(UdXilinxCommandSender, self).__init__()
        self._cfg_manager = cfg_manager
        
    @staticmethod
    def create(cfg_manager):
        return HttpCommandSender(cfg_manager)
    
    def send_command(self, command):
        raise NotImplementedError("This method must be overriden in a subclass.")
    
class HttpCommandSender(UdXilinxCommandSender):
    
    def __init__(self, cfg_manager):
        super(HttpCommandSender, self).__init__(cfg_manager)
        ip = self._cfg_manager.get_value('pic_http_device_ip')
        port = self._cfg_manager.get_value('pic_http_device_port')
        app = self._cfg_manager.get_value('pic_http_device_app')
        self._http_device = _HttpDevice(ip, port, app)
    
    @Override(UdXilinxCommandSender)
    def send_command(self, command):
        self._http_device.send_message(command)
