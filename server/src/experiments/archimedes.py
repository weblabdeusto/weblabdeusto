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
                return "ok"
            else:
                return "ok"


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


