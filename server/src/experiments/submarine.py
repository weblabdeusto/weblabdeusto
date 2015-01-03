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

module_directory = os.path.join(*__name__.split('.')[:-1])

class EventManager(threading.Thread):
    """ Call the tick method of the submarine_experiment every hour """
    def __init__(self, submarine_experiment):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.setName("SubmarineEventManager")
        self.submarine_experiment = submarine_experiment

    def run(self):
        while True:
            now = datetime.datetime.now()
            # Sleep until next hour (61: make sure it's passed)
            time.sleep(60 * (59 - now.minute) + (61 - now.second))
            now = datetime.datetime.now()
            try:
                self.submarine_experiment.tick(now.hour)
            except:
                traceback.print_exc()

class Submarine(Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Submarine, self).__init__(*args, **kwargs)

        thermometer_svg_path = data_filename(os.path.join(module_directory, 'submarine-thermometer.svg'))
        self.thermometer     = open(thermometer_svg_path, "rb").read()

        self._cfg_manager    = cfg_manager

        self._lock           = threading.Lock()
        self._feed_lock      = threading.Lock()
        self._latest_feed_time = datetime.datetime.now()

        self.debug           = self._cfg_manager.get_value('debug', False)
        self.debug_dir       = self._cfg_manager.get_value('debug_dir', None)
        self.real_device     = self._cfg_manager.get_value('real_device', True)
        self.lights_on_time  = self._cfg_manager.get_value('lights_on_time',  10)
        self.lights_off_time = self._cfg_manager.get_value('lights_off_time', 15)
        self.feed_period     = self._cfg_manager.get_value('feed_period', 8)
        self.pic_location    = self._cfg_manager.get_value('submarine_pic_location', 'http://192.168.0.90/')
        self.webcams_info    = self._cfg_manager.get_value('webcams_info', [])
        self.thermometer_path = self._cfg_manager.get_value('thermometer_path', None)

        self.up              = False
        self.down            = False
        self.left            = False
        self.right           = False
        self.forward         = False
        self.backward        = False
        
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

        self.in_use     = False
        self.since_tick = False

        self.correct_lights()
        event_manager = EventManager(self)
        event_manager.start()

    def lights_should_be_on(self):
        """ Lights should be on from 8:00 to 16:00 """
        now = datetime.datetime.now()
        return self.lights_on_time <= now.hour < self.lights_off_time

    def lights_should_be_off(self):
        """ Lights should be off before 8:00 and after 16:00 """
        return not self.lights_should_be_on()

    def tick(self, hour):
        if not self.in_use:
            self.correct_lights()

        if hour % self.feed_period == 0:
            self._lock.acquire()
            while self.in_use:
                time.sleep(0.5)
            try:
                self.feed(True)
            finally:
                self._lock.release()

    def _get_debug_file(self):
        if self.debug_dir is not None and os.path.exists(self.debug_dir):
            now = datetime.datetime.now()
            dir_name = '%s_%s' % (now.year, now.month)
            try:
                os.mkdir(os.path.join(self.debug_dir, dir_name))
            except:
                pass
            debug_fname = '%s.txt' % now.day
            return open(os.path.join(self.debug_dir, dir_name, debug_fname), 'a')
        else:
            return StringIO.StringIO()

    def debug_critical_msg(self, msg):
        f = self._get_debug_file()
        try:
            now = datetime.datetime.now()
            when = now.strftime("%Y-%m-%d %H:%M:%S")
            f.write('%s: %s\n' % (when, msg))
        except:
            traceback.print_exc()
        finally:
            f.close()

    @logged("critical")
    def feed(self, tick):
        with self._feed_lock:
            if tick:
                fed = False
                if not self.since_tick:
                    self._send('FOOD')
                    fed = True
                    self.debug_critical_msg('fed by tick')
                self.since_tick = False
                if fed:
                    return 'fed'
                else:
                    return 'notfed'
            else:
                if not self.since_tick:
                    self._send('FOOD')
                    self.debug_critical_msg('fed by user')
                    self.since_tick = True
                    return 'fed'
                else:
                    current_hour = datetime.datetime.now().hour
                    counter = current_hour + 1
                    while counter < 24 and counter % self.feed_period != 0:
                        counter += 1
                    remaining = (counter - current_hour) % 24
                    return 'notfed:%s' % remaining

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

        # 
        # First, turn on the light, so everyone can see it
        # 
        self._send('LIGHT ON')

        #
        # Then, check the state
        # 
        current_state_str = self._send('STATE')
        current_state = json.loads(current_state_str.replace("'", '"'))

        current_config['light']       = current_state['light']
        if 'temp' in current_state:
            temperature = current_state['temp']
            current_config['temperature'] = temperature
            if self.thermometer_path is not None:
                temperature_image_level = ((temperature - 15) * 10) / 20.0
                if temperature_image_level > 10:
                    temperature_image_level = 10
                elif temperature_image_level < 0:
                    temperature_image_level = 0
                thermo_image = self.thermometer.replace('height="10"', 'height="%s"' % temperature_image_level)
                try:
                    p = subprocess.Popen(["rsvg-convert","--width","40","--height","80","-o",self.thermometer_path], stdin = subprocess.PIPE)
                    p.communicate(thermo_image)
                except:
                    traceback.print_exc()

        self._lock.acquire()
        self.in_use = True
        self._lock.release()

        return json.dumps({ "initial_configuration" : json.dumps(current_config), "batch" : False })

    def _clean(self):
        self._send("CleanInputs")
        self.up              = False
        self.down            = False
        self.left            = False
        self.right           = False
        self.forward         = False
        self.backward        = False

    def correct_lights(self):
        if self.lights_should_be_off():
            self._send("LIGHT OFF")
            self.debug_critical_msg('LIGHT OFF')
        else:
            self._send("LIGHT ON")
            self.debug_critical_msg('LIGHT ON')

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

        if command == 'FOOD':
            msg = self.feed(False)
        elif command in ('LIGHT ON','LIGHT OFF'):
            msg = "received %s" % self._send(command)
            self.debug_critical_msg('User: %s' % command)
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
                    msg = "warning: something incompatible previously sent"  # Forward sent; ignore message
                else:
                    self.backward = True
                    self._send(command)
            else:
                self.backward = False
                self._send(command)
        return msg


    def _send(self, command):
        if self.real_device:
            return self.opener.open(self.pic_location, command).read()
        else:
            if self.debug:
                print "Simulating request...", command
            if command == 'STATE':
                return "{ 'light' : true, 'temp' : 27.4 }"
            else:
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
        self.correct_lights()
        self.in_use = False
        return "ok"


