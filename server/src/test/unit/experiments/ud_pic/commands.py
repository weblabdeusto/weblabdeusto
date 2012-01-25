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
import unittest


import experiments.ud_pic.commands as UdPicBoardCommand
from experiments.ud_pic.commands import ChangeSwitchCommand, SetPulseCommand, AdjustCommand, WriteCommand

import experiments.ud_pic.exc as UdPicExperimentExceptions

class UdPicBoardCommandTestCase(unittest.TestCase):
    def test_ud_pic_board(self):
        UdPicBoardCommand.UdPicBoardCommand("PULSE=3 1000, SWITCH=0 ON, ADJUST=0 0.5")

        self.assertRaises(
                UdPicExperimentExceptions.InvalidUdPicBoardCommandException,
                UdPicBoardCommand.UdPicBoardCommand,
                "foo"
            )

    def test_switch_command(self):
        self.assertEquals(
            "SWITCH=0 ON",
            str(ChangeSwitchCommand("0", "ON"))
        )
        self.assertEquals(
            "SWITCH=0 OFF",
            str(ChangeSwitchCommand("0", "OFF"))
        )
        self.assertEquals(
            "SWITCH=3 ON",
            str(ChangeSwitchCommand("3", "ON"))
        )
        self.assertEquals(
            "SWITCH=3 OFF",
            str(ChangeSwitchCommand("3", "OFF"))
        )

        command = UdPicBoardCommand.UdPicBoardCommand("SWITCH=0 ON")
        self.assertTrue(command._commands[0].switch_on)
        self.assertEquals(0, command._commands[0].number)

        command = UdPicBoardCommand.UdPicBoardCommand("SWITCH=3 OFF")
        self.assertFalse(command._commands[0].switch_on)
        self.assertEquals(3, command._commands[0].number)

    def test_pulse_command(self):
        self.assertEquals(
            "PULSE=0 1000",
            str(SetPulseCommand("0","1000"))
        )
        self.assertEquals(
            "PULSE=0 10000",
            str(SetPulseCommand("0","10000"))
        )
        self.assertEquals(
            "PULSE=3 1",
            str(SetPulseCommand("3","1"))
        )
        self.assertEquals(
            "PULSE=3 100",
            str(SetPulseCommand("3","100"))
        )

        command = UdPicBoardCommand.UdPicBoardCommand("PULSE=3 1")
        self.assertEquals(3, command._commands[0].number)
        self.assertEquals(1, command._commands[0].millis)

        command = UdPicBoardCommand.UdPicBoardCommand("PULSE=0 100")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals(100, command._commands[0].millis)

        command = UdPicBoardCommand.UdPicBoardCommand("PULSE=0 10000")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals(10000, command._commands[0].millis)

    def test_adjust_command(self):
        self.assertEquals(
            "ADJUST=0 0.0",
            str(AdjustCommand("0","0.0"))
        )
        self.assertEquals(
            "ADJUST=0 0.1",
            str(AdjustCommand("0","0.1"))
        )
        self.assertEquals(
            "ADJUST=0 5.0",
            str(AdjustCommand("0","5.0"))
        )
        self.assertEquals(
            "ADJUST=0 4.9",
            str(AdjustCommand("0","4.9"))
        )

        command = UdPicBoardCommand.UdPicBoardCommand("ADJUST=0 5.0")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals(5.0, command._commands[0].power)

        command = UdPicBoardCommand.UdPicBoardCommand("ADJUST=0 0.0")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals(0.0, command._commands[0].power)

        command = UdPicBoardCommand.UdPicBoardCommand("ADJUST=0 2.5")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals(2.5, command._commands[0].power)

    def test_write_command(self):
        self.assertEquals(
            "WRITE=0 this is a sample message EOT",
            str(WriteCommand("0","this is a sample message"))
        )
        self.assertEquals(
            "WRITE=0  EOT",
            str(WriteCommand("0",""))
        )
        self.assertEquals(
            "WRITE=0 hello, IT EOT",
            str(WriteCommand("0","hello, IT"))
        )
        self.assertEquals(
            "WRITE=0 have you tried to turn it off and on again? EOT",
            str(WriteCommand("0","have you tried to turn it off and on again?"))
        )

        command = UdPicBoardCommand.UdPicBoardCommand("WRITE=0 text EOT")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals("text", command._commands[0].text)

        command = UdPicBoardCommand.UdPicBoardCommand("WRITE=0  EOT")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals("", command._commands[0].text)

        command = UdPicBoardCommand.UdPicBoardCommand("WRITE=0 he he he EOT")
        self.assertEquals(0, command._commands[0].number)
        self.assertEquals("he he he", command._commands[0].text)


def suite():
    return unittest.makeSuite(UdPicBoardCommandTestCase)

if __name__ == '__main__':
    unittest.main()


