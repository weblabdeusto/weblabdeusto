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
# Author: Pablo OrduÃ±a <pablo@ordunya.com>
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
from voodoo.override import Override
from experiments.ud_pic18.command_senders import UdXilinxCommandSender
from experiments.ud_pic18.programmers import UdXilinxProgrammer
import os
import tempfile
import voodoo.log as log
import weblab.data.server_type as ServerType
import weblab.experiment.exc as ExperimentExceptions
import weblab.experiment.experiment as Experiment
import weblab.experiment.util as ExperimentUtil

import json

from voodoo.threaded import threaded


# Though it would be slightly more efficient to use single characters, it's a text protocol
# after all, so we will use words for readability.
STATE_NOT_READY = "not_ready"
STATE_PROGRAMMING = "programming"
STATE_READY = "ready"
STATE_FAILED = "failed"


#TODO: which exceptions should the user see and which ones should not?
class UdPic18Experiment(Experiment.Experiment):
    
    
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_get_api(self):
        return "2"
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdPic18Experiment,self).__init__(*args, **kwargs)
        self._coord_address = coord_address
        self._locator = locator
        self._cfg_manager = cfg_manager

        self._programmer     = UdXilinxProgrammer.create(self._cfg_manager)
        self._command_sender = UdXilinxCommandSender.create(self._cfg_manager)
        self.conf_demo       = self._cfg_manager.get_value("demo",         False)
        self.webcam_url      = self._cfg_manager.get_value("webcam_url",   None)
        self.mjpeg_url       = self._cfg_manager.get_value("mjpeg_url",    None)
        self.mjpeg_width     = self._cfg_manager.get_value("mjpeg_width",  None)
        self.mjpeg_height    = self._cfg_manager.get_value("mjpeg_height", None)
        
        self._programming_thread = None
        self._current_state = STATE_NOT_READY
        self._programmer_time = self._cfg_manager.get_value('programmer_time', "25") # Seconds
        self._switches_reversed = self._cfg_manager.get_value('switches_reversed', False) # Seconds
        self.demo = False
        
        file_path = os.path.dirname(__file__) + os.sep + 'demo.hex'
        self.file_content = ExperimentUtil.serialize(open(file_path, "rb").read())

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self, client_arguments, server_arguments, *args, **kwargs):
        experiment_name = json.loads(server_arguments).get('request.experiment_id.experiment_name')

        self.demo = self.conf_demo or experiment_name is not None and (experiment_name.find('demo') >= 0 or experiment_name.find('test') >= 0)
        if self.demo:
            self._programming_thread = self._program_file_t(self.file_content)

        self._current_state = STATE_NOT_READY

        initial_configuration = {}
        if self.webcam_url is not None:
            initial_configuration['webcam'] = self.webcam_url
        if self.mjpeg_url is not None:
            initial_configuration['mjpeg'] = self.mjpeg_url
        if self.mjpeg_width is not None:
            initial_configuration['mjpegWidth'] = self.mjpeg_width
        if self.mjpeg_height is not None:
            initial_configuration['mjpegHeight'] = self.mjpeg_height

        initial_configuration['expected_programming_time'] = self._programmer_time
        return json.dumps({ "initial_configuration" : json.dumps(initial_configuration), "batch" : False })

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
        print "Sending file..."
        if self.demo:
            return "Can not program file. Reason: this experiment is setup as a demo"
        else:
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
            print "Programming file..."
            self._program_file(file_content)
            print "File programmed"
            self._current_state = STATE_READY
        except Exception as e:
            print e
            import traceback
            traceback.print_exc()
            # Note: Currently, running the fake xilinx will raise this exception when
            # trying to do a CleanInputs, for which apparently serial is needed.
            self._current_state = STATE_FAILED
            log.log(UdPic18Experiment, log.level.Warning, "Error programming file: " + str(e) )
            log.log_exc(UdPic18Experiment, log.level.Warning )

    # This is used in the demo experiment
    def _program_file(self, file_content):
        try:
            fd, file_name = tempfile.mkstemp(prefix='pic18_experiment_program', suffix='.hex')
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
                print "File ready in %s" % file_name
                self._programmer.program(file_name)
                print "File sent with programmer: ", self._programmer
            finally:
                os.remove(file_name)
        except Exception as e:
            print "Error sending file"
            import traceback
            traceback.print_exc()
            #TODO: test me
            log.log(
                UdPic18Experiment,
                log.level.Info,
                "Exception joining sending program to device: %s" % e.args[0]
            )
            log.log_exc(
                UdPic18Experiment,
                log.level.Debug
            )
            raise ExperimentExceptions.SendingFileFailureException(
                    "Error sending file to device: %s" % e
                )
        # self._clear()

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
        return "ok"
        
            
   
    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        try:
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
            if command is not None and command.upper().startswith('STRING'):
                command = command + '\0'
            self._command_sender.send_command(command)
        except Exception as e:
            raise ExperimentExceptions.SendingCommandFailureException(
                    "Error sending command to device: %s" % e
                )
