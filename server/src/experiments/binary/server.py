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

class BinaryExperiment(UdXilinxExperiment.UdXilinxExperiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(BinaryExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_start_experiment(self, *args, **kwargs):
        print args, kwargs

        self._clear()
        return "ok"

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        return ""

    def _autoprogram(self):
        GAME_FILE_PATH = os.path.dirname(__file__) + os.sep + "JUEGO4B.jed"
        try:
            serialized_file_content = ExperimentUtil.serialize(open(GAME_FILE_PATH, "r").read())
            super(BinaryExperiment, self).do_send_file_to_device(serialized_file_content, "game")
        except:
            import traceback
            traceback.print_stack()
            import sys
            sys.stdout.flush()

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_get_api(self):
        return "2"

    def do_send_command_to_device(self, command):
        if command == 'AutoProgram':
            self._autoprogram()
        else:
            super(BinaryExperiment, self).do_send_command_to_device(command)
