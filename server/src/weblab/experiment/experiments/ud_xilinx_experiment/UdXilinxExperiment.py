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
import threading
import tempfile

import os
from voodoo.log import logged
import voodoo.log as log

import weblab.experiment.experiments.ud_xilinx_experiment.UdBoardCommand as UdBoardCommand

import weblab.experiment.Experiment                        as Experiment
import weblab.experiment.Util                               as ExperimentUtil
import weblab.experiment.devices.xilinx_impact.XilinxImpact as XilinxImpact
import weblab.experiment.devices.serial_port.SerialPort     as SerialPort

import weblab.experiment.devices.xilinx_impact.XilinxDevices as XilinxDevices

import weblab.data.ServerType                                as ServerType

import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions

from voodoo.gen.caller_checker import caller_check

from voodoo.override import Override



#TODO: which exceptions should the user see and which ones should not?
class UdXilinxExperiment(Experiment.Experiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdXilinxExperiment,self).__init__(*args, **kwargs)

        xilinx_device = cfg_manager.get_value('weblab_xilinx_experiment_xilinx_device')
        port_number   = cfg_manager.get_value('weblab_xilinx_experiment_port_number')
        
        # Expect a certain name for the webcam url config depending on the device name.
        cfg_webcam_url = "%s_webcam_url" % xilinx_device.lower()
        try:
            self.webcam_url = cfg_manager.get_value(cfg_webcam_url)
        except: 
            self.webcam_url = "http://localhost"

        devices = [ i for i in XilinxDevices.getXilinxDevicesValues() if i.name == xilinx_device ] 
        if len(devices) == 1:
            xilinx_device = devices[0]

        self._xilinx_impact = self._create_xilinx_impact(xilinx_device, cfg_manager)
        self._serial_port   = self._create_serial_port()
        self._port_number   = port_number

        self._serial_port_lock = threading.Lock()
        
        
        

    def _create_xilinx_impact(self, xilinx_device, cfg_manager):
        return XilinxImpact.create(xilinx_device, cfg_manager)

    def _create_serial_port(self):
        return SerialPort.SerialPort()

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        try:
            fd, file_name = tempfile.mkstemp(prefix='ud_xilinx_experiment_program',suffix='.' + self._xilinx_impact.get_suffix())
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

                self._xilinx_impact.program_device(file_name)
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
                    "Error sending file to device: %s" % e.args[0]
                )
        self._clear()

    def _clear(self):
        codes = []
        for i in range(10):
            command = UdBoardCommand.ChangeSwitchCommand("on",i)
            codes.append(command.get_code())
            command = UdBoardCommand.ChangeSwitchCommand("off",i)
            codes.append(command.get_code())

        try:
            self._send_codes(codes)
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
                return "WEBCAMURL=" + self.webcam_url
            cmd = UdBoardCommand.UdBoardCommand(command)
            codes = cmd.get_codes()
            self._send_codes(codes)
        except Exception, e:
            raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
    
    def _send_codes(self,codes):
        self._serial_port_lock.acquire()
        try:
            self._serial_port.open_serial_port(self._port_number)
            for i in codes:
                self._serial_port.send_code(i)
            self._serial_port.close_serial_port()
        finally:
            self._serial_port_lock.release()
        
