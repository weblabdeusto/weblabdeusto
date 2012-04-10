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
# Author: Pablo Orduña <pablo@ordunya.com>
#

import urllib2
import json

from voodoo.log import logged
from voodoo.override import Override
from weblab.experiment.experiment import Experiment

class Submarine(Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Submarine, self).__init__(*args, **kwargs)
        self._cfg_manager    = cfg_manager
        self.debug           = self._cfg_manager.get_value('debug', True)
        self.pic_location    = self._cfg_manager.get_value('submarine_pic_location', 'http://192.168.0.90/')
        self.webcam_url      = self._cfg_manager.get_value("webcam_url",   None)
        self.mjpeg_url       = self._cfg_manager.get_value("mjpeg_url",    None)
        self.mjpeg_width     = self._cfg_manager.get_value("mjpeg_width",  None)
        self.mjpeg_height    = self._cfg_manager.get_value("mjpeg_height", None)

    @Override(Experiment)
    @logged("info")
    def do_start_experiment(self, *args, **kwargs):
        """
        Callback run when the experiment is started.
        """
        if self.debug:
            print "[Submarine*] do_start_experiment called"

        initial_configuration = {}
        if self.webcam_url is not None:
            initial_configuration['webcam'] = self.webcam_url
        if self.mjpeg_url is not None:
            initial_configuration['mjpeg'] = self.mjpeg_url
        if self.mjpeg_width is not None:
            initial_configuration['mjpegWidth'] = self.mjpeg_width
        if self.mjpeg_height is not None:
            initial_configuration['mjpegHeight'] = self.mjpeg_height

        return json.dumps({ "initial_configuration" : json.dumps(initial_configuration), "batch" : False })

    @Override(Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if self.debug:
            print "[Submarine*] do_send_command_to_device called"

        if command in ('UP ON','UP OFF','DOWN ON','DOWN OFF','FORWARD ON','FORWARD OFF','BACKWARD ON','BACKWARD OFF','LEFT ON','LEFT OFF','RIGHT ON','RIGHT OFF'):
            return urllib2.urlopen(self.pic_location, command).read()

        return "error:unknown command"


    @Override(Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        """
        Callback for when the client sends a file to the experiment
        server.
        """
        if self.debug:
            print "[Submarine*] do_send_file_to_device called"
        return "Ok"


    @Override(Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if self.debug:
            print "[Submarine*] do_dispose called"
        return "Ok"


