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
from weblab.experiment.experiments.ud_xilinx_experiment.UdXilinxCommandSenders import UdXilinxCommandSender
from weblab.experiment.experiments.ud_xilinx_experiment.UdXilinxProgrammers import UdXilinxProgrammer
import os
import tempfile
import voodoo.log as log
import weblab.data.ServerType as ServerType
import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions
import weblab.experiment.Experiment as Experiment
import weblab.experiment.Util as ExperimentUtil
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

        self._xilinx_device, self._xilinx_impact = self._load_xilinx_device()
        self._programmer = self._load_programmer()
        self._command_sender = self._load_command_sender()
        self.webcam_url = self._load_webcam_url()
        
    def _load_xilinx_device(self):
        device_name = self._cfg_manager.get_value('weblab_xilinx_experiment_xilinx_device')
        devices = [ i for i in XilinxDevices.getXilinxDevicesValues() if i.name == device_name ]
        if len(devices) == 1:
            return devices[0], XilinxImpact.create(devices[0], self._cfg_manager)
        else:
            raise UdXilinxExperimentExceptions.InvalidXilinxDeviceException(device_name)
        
    def _load_programmer(self):
        device_name = self._cfg_manager.get_value('xilinx_device_to_program')
        return UdXilinxProgrammer.create(device_name, self._cfg_manager, self._xilinx_impact)
        
    def _load_command_sender(self):
        device_name = self._cfg_manager.get_value('xilinx_device_to_send_commands')
        return UdXilinxCommandSender.create(device_name, self._cfg_manager)
        
    def _load_webcam_url(self):
        cfg_webcam_url = "%s_webcam_url" % self._xilinx_device.name.lower()        
        return self._cfg_manager.get_value(cfg_webcam_url, "http://localhost")
    
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        self._program_file(file_content)

    # This is used in the demo experiment
    def _program_file(self, file_content):
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
        # As soon as our PLD hardware supports the CleanInputs command, we'll be able to remove this
        if self._xilinx_device == XilinxDevices.PLD:
            try:
                for i in range(10):
                    self._command_sender.send_command(str(UdBoardCommand.ChangeSwitchCommand("on",i)))
                    self._command_sender.send_command(str(UdBoardCommand.ChangeSwitchCommand("off",i)))
            except Exception, e:
                raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
        else:
            try:
                self._command_sender.send_command("CleanInputs")
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
            self._command_sender.send_command(command)
        except Exception, e:
            raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
