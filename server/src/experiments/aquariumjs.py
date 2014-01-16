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
import urllib2
import threading
import traceback

from voodoo.log import logged
from voodoo.override import Override
from weblab.experiment.concurrent_experiment import ConcurrentExperiment

COLORS = {
    'white'  : 1,
    'yellow' : 2,
    'blue'   : 3,
    'red'    : 4,
}

FORCE = {
    'white'  : '3',
    'yellow' : '3',
    'blue'   : '3',
    'red'    : '3',
}

class Proxy(object):

    def __init__(self, url, fake):
        self.fake   = fake
        self.url    = url
        self.opener = urllib2.build_opener(urllib2.ProxyHandler({}))

    def move_ball(self, ball, on):
        # 192.168.0.130:8000/MOVE/{MODE}/{BALL}/{TURNS}
        mode = 'U' if on else 'D'
        ball_number = COLORS[ball]
        force = FORCE[ball]
        try:
            self._process("%s/MOVE/%s/%s/%s" % (self.url, mode, ball_number, force), get = False)
        except:
            traceback.print_exc()

    def process_image(self):
        try:
            content_str = self._process("http://192.168.0.155:7777/image", get = True)
            content = json.loads(content_str)

            base_path = 'https://www.weblab.deusto.es/aquarium'

            return (base_path + content['url_processed']), (base_path + content['url_original'])
        except:
            traceback.print_exc()
            return "error-processing-image", "error-processing-image"

    def get_status(self):
        try:
            content_str = self._process("%s/ballStatus/ALL" % self.url, get = True)
            content = json.loads(content_str)
            white, yellow, blue, red = content['Balls']
            return {
                'white'  : white  == 0,
                'yellow' : yellow == 0,
                'blue'   : blue   == 0,
                'red'    : red    == 0,
            }
        except:
            traceback.print_exc()
            return {
                'white' : True,
                'yellow': True,
                'blue'  : True,
                'red'   : True,
            }

    def _process(self, url, get):
        if self.fake:
            print "[aquarium] Simulating %s call to:" % ('GET' if get else 'POST'), url
            return json.dumps({'Balls' : [0,0,0,0]})
        else:
            print "[aquarium] Calling:", url
            if get:
                urlobj = self.opener.open(url)
            else:
                urlobj = self.opener.open(url, '{}')
            return urlobj.read().replace("'",'"')

class StatusManager(object):

    def __init__(self, proxy):
        self._proxy = proxy

        self._ops_locks = {}

        for color in COLORS:
            self._ops_locks[color] = threading.Lock()

    def move(self, ball, on):
        with self._ops_locks[ball]:
            self._proxy.move_ball(ball, on)

    def get_status(self):
        return self._proxy.get_status()


class Aquarium(ConcurrentExperiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Aquarium, self).__init__(*args, **kwargs)

        self._cfg_manager    = cfg_manager
        
        self.fake            = self._cfg_manager.get_value('fake', True)

        self.proxy = Proxy('http://192.168.0.130:8000', self.fake)

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

        self._status = StatusManager(self.proxy)


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

        if command == 'get-status':
            return json.dumps(self._status.get_status())
        elif command.startswith('ball:'):
            try:
                _, ball, on = command.split(':')
            except:
                traceback.print_exc()
                return "ERROR:Invalid ball command"

            if not ball.lower() in COLORS:
                return "ERROR:Invalid ball color"

            if not on.lower() in ('true','false'):
                return "ERROR:Invalid state"

            on   = on.lower() == 'true'
            ball = ball.lower()
            
            self._status.move(ball, on)

            return json.dumps(self._status.get_status())
        elif command == 'process':
            return json.dumps(self.proxy.process_image())

        return 'ERROR:Invalid command'


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


