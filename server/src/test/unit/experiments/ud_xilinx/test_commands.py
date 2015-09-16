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
from __future__ import print_function, unicode_literals
import unittest

import experiments.ud_xilinx.command as UdBoardCommand
from experiments.ud_xilinx.command import UdBoardSimpleCommand
from experiments.ud_xilinx.command import ChangeSwitchCommand, SetPulseCommand, ClockActivationCommand, ClockDeactivationCommand

import experiments.ud_xilinx.exc as UdXilinxExperimentErrors

class UdBoardCommandTestCase(unittest.TestCase):
    def test_udboard(self):
        cmd = UdBoardCommand.UdBoardCommand("SetPulse on 3, ChangeSwitch on 0, ClockActivation on 250")

        codes = cmd.get_codes()
        self.assertEquals(
                codes,
                (27,1,32)
            )

        self.assertRaises(
                UdXilinxExperimentErrors.InvalidUdBoardCommandError,
                UdBoardCommand.UdBoardCommand,
                "foo"
            )

    def test_str(self):
        self.assertEquals(
            "ChangeSwitch on 0",
            str(ChangeSwitchCommand("on",0))
        )
        self.assertEquals(
            "ChangeSwitch off 0",
            str(ChangeSwitchCommand("off",0))
        )
        self.assertEquals(
            "ChangeSwitch on 9",
            str(ChangeSwitchCommand("on",9))
        )
        self.assertEquals(
            "ChangeSwitch off 9",
            str(ChangeSwitchCommand("off",9))
        )
        # SetPulse
        self.assertEquals(
            "SetPulse on 0",
            str(SetPulseCommand("on",0))
        )
        self.assertEquals(
            "SetPulse off 0",
            str(SetPulseCommand("off",0))
        )
        self.assertEquals(
            "SetPulse on 3",
            str(SetPulseCommand("on",3))
        )
        self.assertEquals(
            "SetPulse off 3",
            str(SetPulseCommand("off",3))
        )
        # ClockActivation
        self.assertEquals(
            "ClockActivation on 250",
            str(ClockActivationCommand(250))
        )
        self.assertEquals(
            "ClockActivation on 500",
            str(ClockActivationCommand(500))
        )
        self.assertEquals(
            "ClockActivation on 2000",
            str(ClockActivationCommand(2000))
        )
        self.assertEquals(
            "ClockActivation off",
            str(ClockDeactivationCommand())
        )


    def test_bounds(self):
        # ChangeSwitch
        self.assertEquals(
            1,
            UdBoardSimpleCommand.create("ChangeSwitch on 0").get_code()
        )
        self.assertEquals(
            2,
            UdBoardSimpleCommand.create("ChangeSwitch off 0").get_code()
        )
        self.assertEquals(
            19,
            UdBoardSimpleCommand.create("ChangeSwitch on 9").get_code()
        )
        self.assertEquals(
            20,
            UdBoardSimpleCommand.create("ChangeSwitch off 9").get_code()
        )
        # SetPulse
        self.assertEquals(
            21,
            UdBoardSimpleCommand.create("SetPulse on 0").get_code()
        )
        self.assertEquals(
            22,
            UdBoardSimpleCommand.create("SetPulse off 0").get_code()
        )
        self.assertEquals(
            27,
            UdBoardSimpleCommand.create("SetPulse on 3").get_code()
        )
        self.assertEquals(
            28,
            UdBoardSimpleCommand.create("SetPulse off 3").get_code()
        )
        # ClockActivation
        self.assertEquals(
            32,
            UdBoardSimpleCommand.create("ClockActivation on 250").get_code()
        )
        self.assertEquals(
            33,
            UdBoardSimpleCommand.create("ClockActivation on 500").get_code()
        )
        self.assertEquals(
            36,
            UdBoardSimpleCommand.create("ClockActivation on 2000").get_code()
        )
        self.assertEquals(
            37,
            UdBoardSimpleCommand.create("ClockActivation off").get_code()
        )

# def suite():
#     return unittest.makeSuite(UdBoardCommandTestCase)

if __name__ == '__main__':
    unittest.main()

