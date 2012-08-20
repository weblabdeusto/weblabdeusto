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
import threading

from voodoo.log import logged
from voodoo.lock import locked
from voodoo.override import Override
from weblab.experiment.experiment import Experiment

USE_REAL_DEVICE = True

class Submarine(Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Submarine, self).__init__(*args, **kwargs)
        self._cfg_manager    = cfg_manager

        self._lock           = threading.Lock()

        self.debug           = self._cfg_manager.get_value('debug', True)
        self.pic_location    = self._cfg_manager.get_value('submarine_pic_location', 'http://192.168.0.90/')
        self.webcams_info    = self._cfg_manager.get_value('webcams_info', [])

        self.up              = False
        self.down            = False
        self.left            = False
        self.right           = False
        self.forward         = False
        self.backward        = False

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


    @Override(Experiment)
    @logged("info")
    def do_start_experiment(self, *args, **kwargs):
        """
        Callback run when the experiment is started.
        """
        if self.debug:
            print "[Submarine*] do_start_experiment called"

        self._clean()

        current_config = self.initial_configuration.copy()
        current_config['light'] = not self._send('STATELIGHT').startswith('0')

        return json.dumps({ "initial_configuration" : json.dumps(current_config), "batch" : False })

    def _clean(self):
        self._send("CleanInputs")
        self.up              = False
        self.down            = False
        self.left            = False
        self.right           = False
        self.forward         = False
        self.backward        = False

    @Override(Experiment)
    @logged("info")
    @locked('_lock')
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if self.debug:
            print "[Submarine*] do_send_command_to_device called: %s" % command

        if command not in ('FOOD', 'LIGHT ON', 'LIGHT OFF','UP ON','UP OFF','DOWN ON','DOWN OFF','FORWARD ON','FORWARD OFF','BACKWARD ON','BACKWARD OFF','LEFT ON','LEFT OFF','RIGHT ON','RIGHT OFF'):
            return "error:unknown command"

        msg = "ok"

        if command == 'FOOD' or command in ('LIGHT ON','LIGHT OFF'):
            msg = "received %s" % self._send(command)
        elif command.startswith('UP'):
            if command == 'UP ON':
                if self.up:
                    msg = "duplicated" # Already sent
                elif self.down:
                    msg = "warning: something incompatible previously sent" # Down sent; ignore message
                else:
                    self.up = True
                    self._send(command)
            else:
                self.up = False
                self._send(command)
        elif command.startswith('DOWN'):
            if command == 'DOWN ON':
                if self.down:
                    msg = "duplicated" # Already sent
                elif self.up:
                    msg = "warning: something incompatible previously sent" # Up sent; ignore message
                else:
                    self.down = True
                    self._send(command)
            else:
                self.down = False
                self._send(command)
        elif command.startswith('LEFT'):
            if command == 'LEFT ON':
                if self.left:
                    msg = "duplicated" # Already sent
                elif self.right:
                    msg = "warning: something incompatible previously sent" # Right sent; ignore message
                else:
                    self.left = True
                    self._send(command)
            else:
                self.left = False
                self._send(command)
        elif command.startswith('RIGHT'):
            if command == 'RIGHT ON':
                if self.right:
                    msg = "duplicated" # Already sent
                elif self.left:
                    msg = "warning: something incompatible previously sent" # Left sent; ignore message
                else:
                    self.right = True
                    self._send(command)
            else:
                self.right = False
                self._send(command)
        elif command.startswith('FORWARD'):
            if command == 'FORWARD ON':
                if self.forward:
                    msg = "duplicated" # Already sent
                elif self.backward:
                    msg = "warning: something incompatible previously sent" # Backward sent; ignore message
                else:
                    self.forward = True
                    self._send(command)
            else:
                self.forward = False
                self._send(command)
        elif command.startswith('BACKWARD'):
            if command == 'BACKWARD ON':
                if self.backward:
                    msg = "duplicated" # Already sent
                elif self.forward:
                    msg = "warning: something incompatible previously sent" # Forward sent; ignore message
                else:
                    self.backward = True
                    self._send(command)
            else:
                self.backward = False
                self._send(command)
        return msg


    def _send(self, command):
        if USE_REAL_DEVICE:
            return urllib2.urlopen(self.pic_location, command).read()
        else:
            print "Simulating request...",command
            return "ok"


    @Override(Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        """
        Callback for when the client sends a file to the experiment
        server.
        """
        if self.debug:
            print "[Submarine*] do_send_file_to_device called"
        return "ok"


    @Override(Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if self.debug:
            print "[Submarine*] do_dispose called"
        self._clean()
        return "ok"


