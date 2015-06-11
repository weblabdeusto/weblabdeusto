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

import json
import urllib2

class RoMIEBlocklyExperiment(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(RoMIEBlocklyExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_base_config()

    def read_base_config(self):
        """
        Reads the base config parameters from the config file.
        """
        pass

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
        if(self._cfg_manager.get_value('debug')):
            print "[RoMIE-Blockly] do_start_experiment called"
        return "OK"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if(self._cfg_manager.get_value('debug')):
            print "[RoMIE-Blockly] Command received: %s" % command

        command = json.loads(command)
        print command

        if command['command'] == 'F':
            return urllib2.urlopen(self._cfg_manager.get_value('romie_server')+'f', timeout = 60).read()
        elif command['command'] == 'L':
            return urllib2.urlopen(self._cfg_manager.get_value('romie_server')+'l', timeout = 60).read()
        elif command['command'] == 'R':
            return urllib2.urlopen(self._cfg_manager.get_value('romie_server')+'r', timeout = 60).read()
        return "ERR"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if(self._cfg_manager.get_value('debug')):
            print "[RoMIE-Blockly] do_dispose called"

        return "OK"
