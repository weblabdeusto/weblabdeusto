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

import time

import voodoo.log as log
from voodoo.log import logged
from voodoo.override import Override
from voodoo.gen.caller_checker import caller_check
import weblab.experiment.devices.tftp_device.TFtpDevice as TFtpDevice
import weblab.experiment.devices.http_device.HttpDevice as HttpDevice
import weblab.experiment.experiments.ud_pic_experiment.UdPicBoardCommand as UdPicBoardCommand
import weblab.experiment.experiments.ud_pic_experiment.TFtpProgramSender as TFtpProgramSender
import weblab.experiment.Util as ExperimentUtil
import weblab.data.ServerType as ServerType

import weblab.experiment.Experiment as Experiment

import weblab.exceptions.experiment.ExperimentExceptions as ExperimentExceptions

# TODO: this is wrong. It wouldn't work for multiple pic experiments
TFTP_SERVER_HOSTNAME = 'pic_tftp_server_hostname'
TFTP_SERVER_PORT     = 'pic_tftp_server_port'
TFTP_SERVER_FILENAME = 'pic_tftp_server_filename'
HTTP_SERVER_HOSTNAME = 'pic_http_server_hostname'
HTTP_SERVER_PORT     = 'pic_http_server_port'
HTTP_SERVER_APP      = 'pic_http_server_app'
CFG_WEBCAM_URL       = 'pic_webcam_url'

DEFAULT_SLEEP_TIME   = 5

DEBUG = False

class UdPicExperiment(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdPicExperiment,self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        
        try:
            self.webcam_url = self._cfg_manager.get_value(CFG_WEBCAM_URL)
        except:
            self.webcam_url = 'http://localhost'

        self._initialize_tftp()
        if DEBUG:
            print "TFTP initialized"
        self._initialize_http()
        if DEBUG:
            print "HTTP initialized"
            
        

    def _initialize_tftp(self):
        tftp_server_hostname, tftp_server_port = self._parse_tftp_configuration()
        if DEBUG:
            print "TFTP configuration loaded"
        self._tftp_device = self._create_tftp_device(
                tftp_server_hostname,
                tftp_server_port
            )
        self._tftp_program_sender = TFtpProgramSender.TFtpProgramSender(
                self._tftp_device,
                self._tftp_remote_filename
            )

    def _initialize_http(self):
        http_server_hostname, http_server_port, http_server_app = self._parse_http_configuration()
        if DEBUG:
            print "HTTP configuration loaded"
        self._http_device = self._create_http_device(
                http_server_hostname,
                http_server_port,
                http_server_app
            )

    def _parse_tftp_configuration(self):
        tftp_server_hostname = self._cfg_manager.get_value(TFTP_SERVER_HOSTNAME)
        tftp_server_port     = self._cfg_manager.get_value(TFTP_SERVER_PORT)
        self._tftp_remote_filename =  self._cfg_manager.get_value(TFTP_SERVER_FILENAME)
        return tftp_server_hostname, tftp_server_port

    def _parse_http_configuration(self):
        http_server_hostname = self._cfg_manager.get_value(HTTP_SERVER_HOSTNAME)
        http_server_port     = self._cfg_manager.get_value(HTTP_SERVER_PORT)
        http_server_app      = self._cfg_manager.get_value(HTTP_SERVER_APP)
        return http_server_hostname, http_server_port, http_server_app

    def _create_tftp_device(self, hostname, port):
        # For testing purposes
        return TFtpDevice.TFtpDevice(hostname, port)
        
    def _create_http_device(self, hostname, port, app):
        # For testing purposes
        return HttpDevice.HttpDevice(hostname, port, app)

    @Override(Experiment.Experiment)
    @logged("info")
    @caller_check(ServerType.Laboratory)
    def do_start_experiment(self):
        """ Implemented to avoid the problem related to returning None in XML-RPC """
        if DEBUG:
            print "call received: do_start_experiment"
        return ""
 
    @Override(Experiment.Experiment)
    @logged("info",except_for=(('file_content',1),))
    @caller_check(ServerType.Laboratory)
    def do_send_file_to_device(self, file_content, file_info):
        if DEBUG:
            print "call received: do_send_file_to_device"
        try:
            #TODO: encode? utf8?
            if isinstance(file_content, unicode):
                file_content_encoded = file_content.encode('utf8')
            else:
                file_content_encoded = file_content
            file_content_recovered = ExperimentUtil.deserialize(file_content_encoded)
            reset_command = UdPicBoardCommand.UdPicBoardSimpleCommand.create("RESET")
            if DEBUG:
                print "sending RESET command..."
            reset_response = self._http_device.send_message(str(reset_command))
            if DEBUG:
                print "response received"
            # TODO: Check reset_response (200)
            time.sleep(DEFAULT_SLEEP_TIME)
            if DEBUG:
                print "sending file..."
            self._tftp_program_sender.send_content(file_content_recovered)
            if DEBUG:
                print "file sent"
        except Exception, e:
            log.log(
                UdPicExperiment,
                log.LogLevel.Info,
                "Exception joining sending program to device: %s" % e.args[0]
            )
            log.log_exc(
                UdPicExperiment,
                log.LogLevel.Warning,
            )
            raise ExperimentExceptions.SendingFileFailureException(
                    "Error sending file to device: %s" % e.args[0]
                )

    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        if DEBUG:
            print "call received: do_send_command_to_device"
                   
        if command.startswith('WEBCAMURL'):
            if DEBUG:
                print "WEBCAMURL command received."
            return "WEBCAMURL=" + self.webcam_url
            
        cmds = UdPicBoardCommand.UdPicBoardCommand(command)
        for cmd in cmds.get_commands():
            response = self._http_device.send_message(str(cmd))
            # TODO: check the response code (200)
            #if response.lower() != "ok":
            #   raise UdPicExperimentExceptions.UdPicInvalidResponseException("the ") #TODO: message
            pass

    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_dispose(self):
        """ Implemented to avoid the problem related to returning None in XML-RPC """
        if DEBUG:
            print "called received: do_dispose"
        return ""
    

class UdPicDummyExperiment(Experiment.Experiment):
    """ Dummy Experiment class to debug this experiment in local. """
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdPicDummyExperiment,self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        
        try:
            self.webcam_url = self._cfg_manager.get_value(CFG_WEBCAM_URL)
        except:
            self.webcam_url = 'http://localhost'


    @Override(Experiment.Experiment)
    @logged("info")
    @caller_check(ServerType.Laboratory)
    def do_start_experiment(self):
        print "do_start_experiment()"

    @Override(Experiment.Experiment)
    @logged("info",except_for=(('file_content',1),))
    @caller_check(ServerType.Laboratory)
    def do_send_file_to_device(self, file_content, file_info):
        print "do_send_file_to_device(%s, %s)" % (file_content, file_info)

    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        print "do_send_command_to_device(%s)" % command
        
        if command.startswith('WEBCAMURL'):
            print "WEBCAMURL command received."
            return "WEBCAMURL=" + self.webcam_url
        
    @Override(Experiment.Experiment)
    @logged("info")
    @caller_check(ServerType.Laboratory)
    def do_dispose(self):
        print "do_dispose()"        
