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

from weblab.util import data_filename
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

        self._cfg_manager = cfg_manager

        self.exercises = {
            'bcd'    : ['cod1', 'cod2',     'cod3',    'cod4',  'cod5'],
            'other'  : ['cod1', 'cod_gray', 'cod_xs3', 'cod_gray_xs3'],
        }

        # module_directory = os.path.join(*__name__.split('.')[:-1])
        module_directory = ('experiments', 'binary')
        self.contents = {}
        for values in self.exercises.values():
            for value in values:
                if value not in self.contents:
                    filename = value + '.jed'
                    full_relative_path_tuple = module_directory + (filename,)
                    full_relative_path = os.path.join(*full_relative_path_tuple)
                    file_path = data_filename( full_relative_path )
                    self.contents[value] = open(file_path, 'rb').read()

        self.current_labels = []

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged('info')
    def do_start_experiment(self, client_initial_data, server_initial_data, *args, **kwargs):
        deserialized_client_request = json.loads(client_initial_data)
        exercise = deserialized_client_request.get('exercise', 'bcd')
        self.current_labels = self.exercises.get(exercise, ['Exercise', exercise, 'not found'])

        self._clear()

        initial_configuration = {}
        webcam = self._cfg_manager.get_value('webcam', None)
        if webcam is not None:
            initial_configuration['webcam']  = webcam
#        initial_configuration['mjpeg']       = 'https://cams.weblab.deusto.es/webcam/robot0/video.mjpeg'
#        initial_configuration['mjpegHeight'] = 240
#        initial_configuration['mjpegWidth']  = 320
        initial_configuration['labels']      = self.current_labels
        return json.dumps({ 'initial_configuration' : json.dumps(initial_configuration), 'batch' : False })

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged('info',except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        return 'Sending files not supported by this laboratory'

    def _autoprogram(self, label):
        content = self.contents[label]
        try:
            serialized_file_content = ExperimentUtil.serialize(content)
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
            return self._autoprogram(command[len('label:'):])
        elif command.startswith('switch:'):
            switch_number, on = command[len('switch:'):].split(',')
            switch_number = 5 + int(switch_number)

            new_command = 'ChangeSwitch %s %s' % (on, switch_number)

            return super(BinaryExperiment, self).do_send_command_to_device(new_command)

        elif command.startswith('STATE'):
            return super(BinaryExperiment, self).do_send_command_to_device(command)

