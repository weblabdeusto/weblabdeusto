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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
from voodoo.override import Override
from weblab.exceptions.experiment.experiments.ud_xilinx_experiment import UdXilinxExperimentExceptions
from weblab.experiment.experiments.ud_xilinx_experiment.UdXilinxProgrammers import UdXilinxProgrammer
import os
import tempfile
import threading
import voodoo.log as log
import weblab.data.ServerType as ServerType
import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions
import weblab.experiment.Experiment as Experiment
import weblab.experiment.Util as ExperimentUtil
import weblab.experiment.devices.digilent_adept.DigilentAdept as DigilentAdept
import weblab.experiment.devices.http_device.HttpDevice as HttpDevice
import weblab.experiment.devices.jtag_blazer.JTagBlazer as JTagBlazer
import weblab.experiment.devices.serial_port.SerialPort as SerialPort
import weblab.experiment.devices.xilinx_impact.XilinxDevices as XilinxDevices
import weblab.experiment.devices.xilinx_impact.XilinxImpact as XilinxImpact
import weblab.experiment.experiments.ud_xilinx_experiment.UdBoardCommand as UdBoardCommand


#TODO: which exceptions should the user see and which ones should not?
class UdXilinxExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdXilinxExperiment,self).__init__(*args, **kwargs)
        self._coord_address = coord_address
        self._locator = locator
        self._cfg_manager = cfg_manager

        self._xilinx_device_name, self._xilinx_device = self._load_xilinx_device()
        self._xilinx_impact = self._create_xilinx_impact(self._xilinx_device, cfg_manager)
        
        self._programmer = self._load_programmer()
        self._device_to_send_commands_name, self._device_to_send_commands = self._load_device_to_send_commands()
        self.webcam_url = self._load_webcam_url()
        
        self._serial_port_lock = threading.Lock()
        
    def _load_programmer(self):
        device_name = self._cfg_manager.get_value('xilinx_device_to_program')
        return UdXilinxProgrammer.create(device_name, self._cfg_manager, self._xilinx_impact)
        
    def _load_device_to_send_commands(self):
        device_name = self._cfg_manager.get_value('xilinx_device_to_send_commands')
        if device_name == 'SerialPort':
            self._port_number = self._cfg_manager.get_value('weblab_xilinx_experiment_port_number')
            return device_name, self._create_serial_port()
        elif device_name == 'HttpDevice':
            ip = self._cfg_manager.get_value('xilinx_http_device_ip_' + self._xilinx_device.name)
            port = self._cfg_manager.get_value('xilinx_http_device_port_' + self._xilinx_device.name)
            app = self._cfg_manager.get_value('xilinx_http_device_app_' + self._xilinx_device.name)
            return device_name, self._create_http_device(ip, port, app)
        else:
            raise UdXilinxExperimentExceptions.InvalidDeviceToSendCommandsException("Provided: %s" % device_name)
        
    def _load_xilinx_device(self):
        device_name = self._cfg_manager.get_value('weblab_xilinx_experiment_xilinx_device')
        devices = [ i for i in XilinxDevices.getXilinxDevicesValues() if i.name == device_name ]
        if len(devices) == 1:
            return device_name, devices[0]
        else:
            raise UdXilinxExperimentExceptions.InvalidXilinxDeviceException("Provided: %s" % device_name)
        
    def _load_webcam_url(self):
        # Expect a certain name for the webcam url config depending on the device name.
        cfg_webcam_url = "%s_webcam_url" % self._xilinx_device_name.lower()        
        return self._cfg_manager.get_value(cfg_webcam_url, "http://localhost")
        
    def _create_xilinx_impact(self, xilinx_device, cfg_manager):
        return XilinxImpact.create(xilinx_device, cfg_manager)

    def _create_serial_port(self):
        return SerialPort.SerialPort()

    def _create_jtag_blazer(self, cfg_manager):
        return JTagBlazer.JTagBlazer(cfg_manager)

    def _create_digilent_adept(self, cfg_manager):
        return DigilentAdept.DigilentAdept(cfg_manager)

    def _create_http_device(self, ip, port, app):
        return HttpDevice.HttpDevice(ip, port, app)
    
    def _send_command_to_device(self, command):
        # TODO: Refactor!
        if self._device_to_send_commands_name == 'HttpDevice':
            self._device_to_send_commands.send_message(command)
        else:
            cmd = UdBoardCommand.UdBoardCommand(command)
            codes = cmd.get_codes()
            self._serial_port_lock.acquire()
            try:
                self._device_to_send_commands.open_serial_port(self._port_number)
                for i in codes:
                    self._device_to_send_commands.send_code(i)
                self._device_to_send_commands.close_serial_port()
            finally:
                self._serial_port_lock.release()

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        try:
            fd, file_name = tempfile.mkstemp(prefix='ud_xilinx_experiment_program', suffix='.' + self._xilinx_impact.get_suffix())
            try:
                try:
                    #TODO: encode? utf8?
                    if isinstance(file_content, unicode):
                        file_content_encoded = file_content.encode('utf8')
                    else:
                        file_content_encoded = file_content
                    file_content_recovered = ExperimentUtil.deserialize(file_content_encoded)
                    os.write(fd, file_content_recovered)
                finally:
                    os.close(fd)
                self._programmer.program(file_name)
            finally:
                os.remove(file_name)
        except Exception, e:
            #TODO: test me
            log.log(
                UdXilinxExperiment,
                log.LogLevel.Info,
                "Exception joining sending program to device: %s" % e.args[0]
            )
            log.log_exc(
                UdXilinxExperiment,
                log.LogLevel.Debug
            )
            raise ExperimentExceptions.SendingFileFailureException(
                    "Error sending file to device: %s" % e
                )
        self._clear()

    def _clear(self):
        # Kludge!!
        if self._xilinx_device_name == "PLD":
            try:
                for i in range(10):
                    self._send_command_to_device(str(UdBoardCommand.ChangeSwitchCommand("on",i)))
                    self._send_command_to_device(str(UdBoardCommand.ChangeSwitchCommand("off",i)))
            except Exception, e:
                raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
        else:
            try:
                self._send_command_to_device("CleanInputs")
            except Exception, e:
                raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )

    
    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        try:
            if command == 'WEBCAMURL':
                reply = "WEBCAMURL=" + self.webcam_url
                return reply
            self._send_command_to_device(command)
        except Exception, e:
            raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
