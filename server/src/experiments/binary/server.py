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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import os
import experiments.ud_xilinx.server as UdXilinxExperiment
import weblab.experiment.experiment as Experiment
import weblab.experiment.util as ExperimentUtil

import weblab.data.server_type as ServerType

from voodoo.override import Override
from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
import json

class BinaryExperiment(UdXilinxExperiment.UdXilinxExperiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(BinaryExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)
        self.exercises = {
            'bcd'    : ['cod1', 'cod2',     'cod3',    'cod4',  'cod5'],
            'others' : ['cod1', 'cod_gray', 'cod_xs3', 'cod_gray_xs3'],
        }
        self.current_labels = []

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged('info')
    def do_start_experiment(self, client_initial_data, server_initial_data, *args, **kwargs):
        deserialized_client_request = json.loads(client_initial_data)
        exercise = deserialized_client_request['exercise']
        self.current_labels = self.exercises.get(exercise, ['Exercise', exercise, 'not found'])

        self._clear()

        initial_configuration = {}
        initial_configuration['webcam']      = 'https://www.weblab.deusto.es/webcam/proxied.py/robot1'
        initial_configuration['mjpeg']       = 'https://www.weblab.deusto.es/webcam/robot0/video.mjpeg'
        initial_configuration['mjpegHeight'] = 240
        initial_configuration['mjpegWidth']  = 320
        initial_configuration['labels']      = self.current_labels
        return json.dumps({ 'initial_configuration' : json.dumps(initial_configuration), 'batch' : False })

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged('info',except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        return 'Sending files not supported by this laboratory'

    def _autoprogram(self, label):
        GAME_FILE_PATH = os.path.dirname(__file__) + os.sep + label
        try:
            serialized_file_content = ExperimentUtil.serialize(open(GAME_FILE_PATH, 'r').read())
            super(BinaryExperiment, self).do_send_file_to_device(serialized_file_content, 'game')
        except:
            import traceback
            traceback.print_exc()
            import sys
            sys.stderr.flush()

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged('info')
    def do_get_api(self):
        return '2'

    def do_send_command_to_device(self, command):
        if command.startswith('label:') and command[len('label:'):] in self.current_labels:
            self._autoprogram(command[len('label:'):])
        elif command.startswith('switch:'):
            print command
            switch_number, on = command[len('switch:'):].split(',')

            new_command = 'ChangeSwitch %s %s' % (on, switch_number)
            super(BinaryExperiment, self).do_send_command_to_device(new_command)

