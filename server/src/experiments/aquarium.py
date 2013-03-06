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

import os
import json
import threading

from voodoo.log import logged
from voodoo.override import Override
from weblab.experiment.concurrent_experiment import ConcurrentExperiment

class StatusManager(object):
    def __init__(self):
        self._status_lock = threading.Lock()
        self._status = {
            'red'    : True,
            'green'  : True,
            'blue'   : True,
            'yellow' : True,
        }

    def move(self, ball, on):
        with self._status_lock:
            self._status[ball] = on.lower() == 'on'

    def get_status(self):
        with self._status_lock:
            return self._status.copy()


class Aquarium(ConcurrentExperiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Aquarium, self).__init__(*args, **kwargs)

        self._cfg_manager    = cfg_manager
        self.debug           = self._cfg_manager.get_value('debug', True)
        self.webcams_info    = self._cfg_manager.get_value('webcams_info', [])

        self.initial_configuration = {}
        for pos, webcam_config in enumerate(self.webcams_info):
            num = pos + 1
            webcam_url   = webcam_config.get('webcam_url')
            mjpeg_url    = webcam_config.get('mjpeg_url')
            mjpeg_width  = webcam_config.get('mjpeg_width')
            mjpeg_height = webcam_config.get('mjpeg_height')

            if webcam_url is not None:
                self.initial_configuration['webcam%s' % num] = webcam_url
            if mjpeg_url is not None:
                self.initial_configuration['mjpeg%s' % num] = mjpeg_url
            if mjpeg_width is not None:
                self.initial_configuration['mjpegWidth%s' % num] = mjpeg_width
            if mjpeg_height is not None:
                self.initial_configuration['mjpegHeight%s' % num] = mjpeg_height

        self._status = StatusManager()


    @Override(ConcurrentExperiment)
    @logged("info")
    def do_start_experiment(self, lab_session_id, *args, **kwargs):
        """
        Callback run when the experiment is started.
        """
        if self.debug:
            print "[Aquarium*] do_start_experiment called"

        current_config = self.initial_configuration.copy()
        current_config['status'] = self._status.get_status()

        return json.dumps({ "initial_configuration" : json.dumps(current_config), "batch" : False })

    @Override(ConcurrentExperiment)
    @logged("info")
    def do_send_command_to_device(self, lab_session_id, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if self.debug:
            print "[Aquarium*] do_send_command_to_device called: %s" % command

        return 'ok'


    @Override(ConcurrentExperiment)
    @logged("info")
    def do_send_file_to_device(self, lab_session_id, content, file_info):
        """
        Callback for when the client sends a file to the experiment
        server.
        """
        if self.debug:
            print "[Aquarium*] do_send_file_to_device called"
        return "ok"


    @Override(ConcurrentExperiment)
    @logged("info")
    def do_dispose(self, lab_session_id):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if self.debug:
            print "[Aquarium*] do_dispose called"
        return "ok"


