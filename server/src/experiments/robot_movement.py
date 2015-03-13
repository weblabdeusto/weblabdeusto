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
# Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
#

import weblab.experiment.experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged

import json
import time

DEBUG = True


class RobotMovement(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(RobotMovement, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_base_config()


    def read_base_config(self):
        """
        Reads the base config parameters from the config file. More parameters will be read through
        the same manager from the actual Virtual Machine Manager, and some may be implementation-specific.
        """
        pass

    @Override(Experiment.Experiment)
    @logged("info")
    def do_get_api(self):
        return "2"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self, *args, **kwargs):
        """
        Callback run when the experiment is started.
        """
        if(DEBUG):
            print "[Robot*] do_start_experiment called"
        return json.dumps({ "initial_configuration" : json.dumps({ "webcam" : "https://cams.weblab.deusto.es/webcam/proxied.py/robot1", "mjpeg" : "https://cams.weblab.deusto.es/webcam/robot0/video.mjpeg", "mjpegHeight" : 240, "mjpegWidth" : 320}), "batch" : False })

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if(DEBUG):
            print "[Robot*] do_send_command_to_device called"

        if command == 'WEBCAMURL':
            return "WEBCAMURL=https://cams.weblab.deusto.es/webcam/proxied.py/robot1"
        if command.startswith("program:"):
            print "Programming example"
            time.sleep(3)
            return "ok"
        if command.startswith('move:'):
            where = command[len('move:'):]
            print "Moving " + where
            time.sleep(2)
            return "Command..."
        return "Ok"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        """
        Callback for when the client sends a file to the experiment
        server.
        """
        if(DEBUG):
            print "[Robot*] do_send_file_to_device called"
        return "Ok"


    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if(DEBUG):
            print "[Robot*] do_dispose called"
        return "Ok"


