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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
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
import weblab.experiment.exc as ExperimentExceptions
import weblab.experiment.Experiment as Experiment
import weblab.experiment.Util as ExperimentUtil
import weblab.experiment.devices.xilinx_impact.XilinxDevices as XilinxDevices
import weblab.experiment.devices.xilinx_impact.XilinxImpact as XilinxImpact

from voodoo.threaded import threaded


# Though it would be slightly more efficient to use single characters, it's a text protocol
# after all, so we will use words for readability.
STATE_NOT_READY = "not_ready"
STATE_PROGRAMMING = "programming"
STATE_READY = "ready"
STATE_FAILED = "failed"


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
        
        self._programming_thread = None
        self._current_state = STATE_NOT_READY
        self._programmer_time = self._cfg_manager.get_value('xilinx_programmer_time', "25") # Seconds
        self._switches_reversed = self._cfg_manager.get_value('switches_reversed', False) # Seconds
        
    def _load_xilinx_device(self):
        device_name = self._cfg_manager.get_value('weblab_xilinx_experiment_xilinx_device')
        devices = [ i for i in XilinxDevices.getXilinxDeviceValues() if i == device_name ]
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
        cfg_webcam_url = "%s_webcam_url" % self._xilinx_device.lower()        
        return self._cfg_manager.get_value(cfg_webcam_url, "http://localhost")
    
    def get_state(self):
        return self._current_state
    
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        """
        Will spawn a new thread which will program the xilinx board with the
        provided file.
        """
        self._programming_thread = self._program_file_t(file_content)
        return "STATE=" + STATE_PROGRAMMING
        
    
    @threaded()
    def _program_file_t(self, file_content):
        """
        Running in its own thread, this method will program the board
        while updating the state of the experiment appropriately.
        """
        try:
            self._current_state = STATE_PROGRAMMING
            self._program_file(file_content)
            self._current_state = STATE_READY
        except Exception as e:
            # Note: Currently, running the fake xilinx will raise this exception when
            # trying to do a CleanInputs, for which apparently serial is needed.
            self._current_state = STATE_FAILED
            log.log(UdXilinxExperiment, log.LogLevel.Warning, "Error programming file: " + str(e) )
            log.log_exc(UdXilinxExperiment, log.LogLevel.Warning )

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
        except Exception as e:
            
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
        try:
            self._command_sender.send_command("CleanInputs")
        except Exception as e:
            raise ExperimentExceptions.SendingCommandFailureException(
                "Error sending command to device: %s" % e
            )
            
    
    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        We make sure that the board programming thread has finished, just
        in case the experiment finished early and its still on it.
        """
        if self._programming_thread is not None:
            self._programming_thread.join()
            # Cleaning references
            self._programming_thread = None
        
            
    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self, *args, **kwargs):
        self._current_state = STATE_NOT_READY

    
    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        try:
            # Provide the URL address that the client will display.
            if command == 'WEBCAMURL':
                reply = "WEBCAMURL=" + self.webcam_url
                return reply
            # Provide how long in seconds will the programmer take (approximately)
            if command == 'EXPECTED.PROGRAMMING.TIME':
                reply = "EXPECTED=%s" % self._programmer_time
                return reply
            # Reply with the current state of the experiment. Particularly, the clients 
            # will need to know whether the programming has been done and whether we are 
            # hence ready to start receiving real commands.
            if command == 'STATE':
                reply = "STATE="+ self._current_state
                return reply
            
            # Otherwise we assume that the command is intended for the actual device handler
            # If it isn't, it throw an exception itself.

            if self._switches_reversed:
               if command.startswith("ChangeSwitch"):
                   command = command.replace(command[-1], str(9 - int(command[-1])))
            self._command_sender.send_command(command)
        except Exception as e:
            raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
