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
# Author: Luis Rodriguez <luis.rodriguezgil@deusto.es>
#
import base64

import os
import traceback
import urllib2
import json
import threading
import datetime
import time
import StringIO
import subprocess

from weblab.util import data_filename
from voodoo.log import logged
from voodoo.lock import locked
from voodoo.override import Override
from weblab.experiment.experiment import Experiment

#module_directory = os.path.join(*__name__.split('.')[:-1])


class Archimedes(Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Archimedes, self).__init__(*args, **kwargs)

        self.DEBUG = True
        self.real_device = True

        self._lock = threading.Lock()

#        thermometer_svg_path = data_filename(os.path.join(module_directory, 'submarine-thermometer.svg'))

        self._cfg_manager    = cfg_manager

        # IP of the board, raspberry, beagle, or whatever.
        self.board_location    = self._cfg_manager.get_value('archimedes_board_location', 'http://192.168.0.161:2001/')
        self.webcams_info    = self._cfg_manager.get_value('webcams_info', [])
        
        self.opener          = urllib2.build_opener(urllib2.ProxyHandler({}))
        
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
        if self.DEBUG:
            print "[Archimedes] do_start_experiment called"

        current_config = self.initial_configuration.copy()

        return json.dumps({"initial_configuration": json.dumps(current_config), "batch": False})



    @Override(Experiment)
    @logged("info")
    @locked('_lock')
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if self.DEBUG:
            print "[Archimedes]: do_send_command_to_device called: %s" % command

        if command == "UP":
            return self._send("up")
        elif command == "DOWN":
            return self._send("down")
        elif command == "LEVEL":
            resp = self._send("level")
            num = resp.split("=")[1]
            return num
        elif command == "LOAD":
            resp = self._send("load")
            num = resp.split("=")[1]
            return num
        elif command == "IMAGE":
            resp = self._send("image")
            img = base64.b64encode(resp)
            return img
        else:
            return "Unknown command. Allowed commands: " + "[UP | DOWN | LEVEL | LOAD | IMAGE]"

    def _send(self, command):
        if self.real_device:
            print "[Archimedes]: Sending to board: ", command
            return self.opener.open(self.board_location + command).read()
        else:
            print "[Archimedes]: Simulating request: ", command
            if command == 'UP':
                return "ball_up"
            elif command == 'DOWN':
                return "ball_down"
            elif command == 'LEVEL':
                return "1200"
            elif command == 'LOAD':
                return "1300"
            elif command == "IMAGE":
                # A test image.
                img = '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'
                return img
            return "UNKNOWN"


    @Override(Experiment)
    @logged("info")
    def do_send_file_to_device(self, content, file_info):
        """
        Callback for when the client sends a file to the experiment
        server.
        """
        if self.DEBUG:
            print "[Archimedes] do_send_file_to_device called"
        return "ok"


    @Override(Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if self.DEBUG:
            print "[Archimedes] do_dispose called"
        return "ok"


if __name__ == "__main__":
    from voodoo.configuration import ConfigurationManager
    from voodoo.sessions.session_id import SessionId

    cfg_manager = ConfigurationManager()
    #cfg_manager._set_value("archimedes_board_location", "http://localhost:2000")
    experiment = Archimedes(None, None, cfg_manager)
    lab_session_id = SessionId('my-session-id')

    start = experiment.do_start_experiment()
    up_resp = experiment.do_send_command_to_device("UP")
    print up_resp
    down_resp = experiment.do_send_command_to_device("DOWN")
    print down_resp
    level_resp = experiment.do_send_command_to_device("LEVEL")
    print level_resp
    load_resp = experiment.do_send_command_to_device("LOAD")
    print load_resp
    image_resp = experiment.do_send_command_to_device("IMAGE")
    print image_resp

    f = file("/tmp/img.html", "w+")
    f.write("""
        <html><body><img alt="embedded" src="data:image/jpg;base64,%s"/></body></html>
        """ % (image_resp)
    )
    f.close()


