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
#         Luis Rodriguez-Gil <luis.rodriguezgil@deusto.es>
#

from abc import ABCMeta, abstractmethod
from voodoo.override import Override
from experiments.ud_xilinx.exc import InvalidDeviceToProgramError
from weblab.experiment.devices.xilinx.programmers.digilent_adept import DigilentAdept
from weblab.experiment.devices.xilinx.programmers.jtag_blazer import JTagBlazer
from weblab.experiment.devices.xilinx.programmers.xcs3prog import Xcs3prog
from weblab.experiment.devices.xilinx.programmers.xilinx_impact.impact import XilinxImpact


class XilinxProgrammer(object):
    """
    Generic Programmer class. A Programmer is the class that can program a logic into a specific hardware board.
    Through this class it is possible to automagically instance the right class according to its parameters.
    """

    __metaclass__ = ABCMeta

    def __init__(self, cfg_manager, xilinx_board_type):
        super(XilinxProgrammer, self).__init__()
        self._cfg_manager = cfg_manager
        self._xilinx_board_type = xilinx_board_type

    @staticmethod
    def create(programmer_name, cfg_manager, xilinx_board_type):
        if programmer_name == 'XilinxImpact':
            return XilinxImpactProgrammer(cfg_manager, xilinx_board_type)
        elif programmer_name == 'JTagBlazer':
            return JTagBlazerSvfProgrammer(cfg_manager, xilinx_board_type)
        elif programmer_name == 'DigilentAdept':
            return DigilentAdeptSvfProgrammer(cfg_manager, xilinx_board_type)
        elif programmer_name == 'Xcs3prog':
            return Xcs3progProgrammer(cfg_manager, xilinx_board_type)
        else:
            print "Invalid device: " + programmer_name
            raise InvalidDeviceToProgramError(programmer_name)

    @abstractmethod
    def program(self, file_name):
        pass

    @abstractmethod
    def get_suffix(self):
        pass



class Xcs3progProgrammer(XilinxProgrammer):
    """
    New programmer (Sept 2015). Should work with FPGAs. Originally added to support the Elevator FPGA.
    """

    def __init__(self, cfg_manager, xilinx_board_type):
        super(Xcs3progProgrammer, self).__init__(cfg_manager, xilinx_board_type)
        self._xc3sprog_device = Xcs3prog(cfg_manager)

    @Override(XilinxProgrammer)
    def program(self, file_name):
        self._xc3sprog_device.program_device(file_name, self._xilinx_board_type)

    @Override(XilinxProgrammer)
    def get_suffix(self):
        if self._xilinx_board_type == 'FPGA':
            return ".bit"
        else:
            return ".jed"


class XilinxImpactProgrammer(XilinxProgrammer):

    def __init__(self, cfg_manager, xilinx_board_type):
        super(XilinxImpactProgrammer, self).__init__(cfg_manager, xilinx_board_type)
        self._xilinx_impact_device = XilinxImpact(cfg_manager)

    @Override(XilinxProgrammer)
    def program(self, file_name):
        self._xilinx_impact_device.program_device(file_name)


    @Override(XilinxProgrammer)
    def get_suffix(self):
        if self._xilinx_board_type == 'FPGA':
            return ".bit"
        else:
            return ".jed"



class JTagBlazerSvfProgrammer(XilinxProgrammer):
    """
    Note Sept 2015: This class may no longer work. Originally it relied on Xilinx Impact, for some reason.
    Maybe it's just because Impact is needed to convert to SVF or whatever that is, but the programming itself is
    still handled by JTag.
    """

    def __init__(self, cfg_manager, xilinx_board_type):
        super(JTagBlazerSvfProgrammer, self).__init__(cfg_manager, xilinx_board_type)
        self._jtag_blazer = JTagBlazer(cfg_manager)
        self._device_ip = self._cfg_manager.get_value('xilinx_jtag_blazer_device_ip')

    @Override(XilinxProgrammer)
    def program(self, file_name):
        raise Exception("JTAG IS SOMEWHAT DEPRECATED")
        # self._xilinx_impact_device.source2svf(file_name)
        svf_file_name = file_name.replace("."+self._xilinx_impact_device.get_suffix(), ".svf")
        self._jtag_blazer.program_device(svf_file_name, self._device_ip)


    @Override(XilinxProgrammer)
    def get_suffix(self):
        if self._xilinx_board_type == 'FPGA':
            return ".bit"
        else:
            return ".jed"


class DigilentAdeptSvfProgrammer(XilinxProgrammer):

    def __init__(self, cfg_manager, xilinx_board_type):
        super(DigilentAdeptSvfProgrammer, self).__init__(cfg_manager, xilinx_board_type)
        self._digilent_adept = DigilentAdept(cfg_manager)

    @Override(XilinxProgrammer)
    def program(self, file_name):
        # self._xilinx_impact_device.source2svf(file_name)
        # svf_file_name = file_name.replace("."+self._xilinx_impact_device.get_suffix(), ".svf")
        # self._digilent_adept.program_device(svf_file_name)
        self._digilent_adept.program_device(file_name)


    @Override(XilinxProgrammer)
    def get_suffix(self):
        if self._xilinx_board_type == 'FPGA':
            return ".bit"
        else:
            return ".jed"



