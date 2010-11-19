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

import weblab.experiment.Experiment                         as Experiment
import weblab.experiment.Util                               as ExperimentUtil
import weblab.experiment.devices.xilinx_impact.XilinxImpact as XilinxImpact
import weblab.experiment.devices.serial_port.SerialPort     as SerialPort
import weblab.experiment.devices.jtag_blazer.JTagBlazer     as JTagBlazer
import weblab.experiment.devices.http_device.HttpDevice     as HttpDevice
import weblab.experiment.devices.digilent_adept.DigilentAdept as DigilentAdept

import weblab.experiment.devices.xilinx_impact.XilinxDevices as XilinxDevices

import weblab.data.ServerType                                as ServerType

import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions

from voodoo.gen.caller_checker import caller_check

from voodoo.override import Override


DEBUG = False


#TODO: which exceptions should the user see and which ones should not?
class UdXilinxExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdXilinxExperiment,self).__init__(*args, **kwargs)
        
        self._cfg_manager = cfg_manager

        xilinx_device = cfg_manager.get_value('weblab_xilinx_experiment_xilinx_device')
        
        # Expect a certain name for the webcam url config depending on the device name.
        cfg_webcam_url = "%s_webcam_url" % xilinx_device.lower()
        try:    
            self.webcam_url = cfg_manager.get_value(cfg_webcam_url)
            if DEBUG:
                print "[DEBUG] Webcam set: " + self.webcam_url
                print "[DEBUG] Var name: " + cfg_webcam_url
        except:
            if DEBUG:
                print "[DEBUG] Couldn't set webcam url properly."
                self.webcam_url = "http://localhost"

        devices = [ i for i in XilinxDevices.getXilinxDevicesValues() if i.name == xilinx_device ]
        if len(devices) == 1:
            self._xilinx_device = devices[0]
        else:
            self._xilinx_device = None

        self._use_jtag_blazer = cfg_manager.get_value('xilinx_use_jtag_blazer_to_program')
        self._use_digilent_adept = cfg_manager.get_value('xilinx_use_digilent_adept_to_program')
        self._use_http = cfg_manager.get_value('xilinx_use_http_to_send_commands')

        self._xilinx_impact = self._create_xilinx_impact(self._xilinx_device, cfg_manager)
        if self._use_jtag_blazer:
            self._jtag_blazer = self._create_jtag_blazer(cfg_manager)
	elif self._use_digilent_adept:
            self._digilent_adept = self._create_digilent_adept(cfg_manager)
        
        if self._use_http:
            http_ip = cfg_manager.get_value('xilinx_http_device_ip_' + self._xilinx_device.name)
            http_port = cfg_manager.get_value('xilinx_http_device_port_' + self._xilinx_device.name)
            http_app = cfg_manager.get_value('xilinx_http_device_app_' + self._xilinx_device.name)
            self._http_device = self._create_http_device(http_ip, http_port, http_app)
        else:
            self._port_number = cfg_manager.get_value('weblab_xilinx_experiment_port_number')
            self._serial_port = self._create_serial_port()
        
        

        self._serial_port_lock = threading.Lock()
        
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
    
    def _program_device(self, file_name):
        if self._use_jtag_blazer:
            self._xilinx_impact.source2svf(file_name)
            svf_file_name = file_name.replace("."+self._xilinx_impact.get_suffix(), ".svf")
            device_ip = self._cfg_manager.get_value('xilinx_jtag_blazer_device_ip_' + self._xilinx_device.name)
            self._jtag_blazer.program_device(svf_file_name, device_ip)
        elif self._use_digilent_adept:
            self._xilinx_impact.source2svf(file_name)
            svf_file_name = file_name.replace("."+self._xilinx_impact.get_suffix(), ".svf")
            self._digilent_adept.program_device(svf_file_name)
        else:
            self._xilinx_impact.program_device(file_name)
    
    def _send_command_to_device(self, command):
        if self._use_http:
            self._http_device.send_message(command)
        else:
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
                self._program_device(file_name)
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
        xilinx_device = self._cfg_manager.get_value('weblab_xilinx_experiment_xilinx_device')
        if xilinx_device == "PLD":
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
                if DEBUG:
                    print '[Debug] Sending WEBCAMURL command: ' + reply
                return reply
            self._send_command_to_device(command)
        except Exception, e:
            raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
