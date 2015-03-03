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
# Author: Iban Eguia <iban.eguia@opendeusto.es>
#

import weblab.experiment.experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged

import urllib2
import json
import time

# Actually defined through the configuration.
DEBUG = True

class NewIncubatorExperiment(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(NewIncubatorExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_base_config()

    def read_base_config(self):
        """
        Reads the base config parameters from the config file.
        """
        self.server = self._cfg_manager.get_value('server')

    @Override(Experiment.Experiment)
    @logged("info")
    def do_get_api(self):
        return "2"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self, client_initial_data, server_initial_data):
        """
        Callback run when the experiment is started.
        """
        if(DEBUG):
            print "[Incubator] do_start_experiment called"

        self.lightStatus = urllib2.urlopen("%slstatus" % self.server).read() == 'ON'
        self.lastCheck = time.time()
        self.lastLight = 0

        return ""

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if(DEBUG):
            print "[Incubator] Command received: %s" % command

        if command == 'L_ON':
            if (self.lastLight < (time.time()-10)):
                self.lightStatus = True
                self.lastLight = time.time()
                urllib2.urlopen("%slon" % self.server).read()

            return self.lightStatus
        elif command == 'L_OFF':
            if (self.lastLight < (time.time()-10)):
                self.lightStatus = True
                self.lastLight = time.time()
                urllib2.urlopen("%slon" % self.server).read()

            return self.lightStatus
        elif command == 'DATA':
            if (self.lastCheck < (time.time()-2)):
                self.data = json.loads(urllib2.urlopen("%sdata" % self.server).read())
            return json.dumps(self.data)

        elif command == 'LIGHT_STATUS':
            return self.lighStatus

        return "ERROR"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if(DEBUG):
            print "[Incubator] do_dispose called"

        return "OK"
