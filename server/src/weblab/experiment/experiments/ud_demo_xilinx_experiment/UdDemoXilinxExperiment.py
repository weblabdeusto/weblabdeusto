#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
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

from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
from voodoo.override import Override
from voodoo.threaded import threaded
import weblab.experiment.experiments.ud_xilinx_experiment.UdXilinxExperiment as UdXilinxExperiment
import os
import weblab.data.ServerType as ServerType
import weblab.experiment.Util as ExperimentUtil

class UdDemoXilinxExperiment(UdXilinxExperiment.UdXilinxExperiment):

    FILES = {
            'PLD'  : 'cpld.jed',
            'FPGA' : 'fpga.bit',
        }
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdDemoXilinxExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)
        file_path = os.path.dirname(__file__) + os.sep + self.FILES[self._xilinx_device.name]
        self.file_content = ExperimentUtil.serialize(open(file_path, "rb").read())
        
    @Override(UdXilinxExperiment.UdXilinxExperiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_start_experiment(self):
        self._program_handler = self._t_program_file(self.file_content)

    @Override(UdXilinxExperiment.UdXilinxExperiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_dispose(self):
        self._program_handler.join()

    @threaded()
    def _t_program_file(self):
        self._program_file(self.file_content)

    @Override(UdXilinxExperiment.UdXilinxExperiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        pass

    @logged("info")
    @Override(UdXilinxExperiment.UdXilinxExperiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        if command == 'EXPERIMENT_FINISHED':
            if self._program_handler.isAlive():
                return "false"
            else:
                return "true"
        return super(UdDemoXilinxExperiment, self).do_send_command_to_device(command)

