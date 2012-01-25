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
import re

import experiments.ud_pic.exc as UdPicExperimentExceptions

class UdPicBoardCommand(object):
    _REGEX_FORMAT="^((%(complete-syntax)s, )*%(complete-syntax)s)$" 
    @staticmethod
    def get_syntax():
        return UdPicBoardCommand._REGEX_FORMAT % { 
            'complete-syntax' : UdPicBoardSimpleCommand.get_full_syntax()
        }

    def __init__(self, command):
        mo = re.match(UdPicBoardCommand.get_syntax(), command)
        if mo == None:
            raise UdPicExperimentExceptions.InvalidUdPicBoardCommandException(
                    "Invalid command format; %s required" % UdPicBoardCommand.get_syntax()
                )
        self._commands = []
        for i in command.split(', '):
            self._commands.append(UdPicBoardSimpleCommand.create(i))

    def get_commands(self):
        return self._commands[:]

class UdPicBoardSimpleCommand(object):

    SUBCLASSES = ()

    def __init__(self):
        super(UdPicBoardSimpleCommand,self).__init__()

    @staticmethod
    def create(str_command):
        for SubClass in UdPicBoardSimpleCommand.SUBCLASSES:
            mo = re.match(SubClass.Syntax, str_command+"=")
            if mo != None:
                return SubClass(*(mo.groups()))

    @staticmethod
    def get_full_syntax():
        syntax = '('
        for i in UdPicBoardSimpleCommand.SUBCLASSES:
            syntax += '%s|' % i.Syntax
        return syntax[:-1] + ')'

def on_off_to_bool(on_off):
    if on_off.upper() == "ON":
        return True
    elif on_off.upper() == "OFF":
        return False
    else:
        raise UdPicExperimentExceptions.IllegalStatusUdPicBoardCommandException("%s is not on nor off" % on_off)

def bool_to_on_off(on_off):
    if on_off:
        return "ON"
    else:
        return "OFF"

#####################################################
######    UdPicBoardSimpleCommand Implementors   #######
#####################################################

class ChangeSwitchCommand(UdPicBoardSimpleCommand):

    Syntax = "SWITCH=([0-4]) (ON|OFF)"

    def __init__(self, number, switch_on):
        super(ChangeSwitchCommand,self).__init__()
        self.switch_on = on_off_to_bool(switch_on)
        self.number = int(number)

    def __str__(self):
        return "SWITCH=%s %s" % (
                self.number,
                bool_to_on_off(self.switch_on)
            )

#Register ChangeSwitchCommand
UdPicBoardSimpleCommand.SUBCLASSES += (ChangeSwitchCommand,)



class SetPulseCommand(UdPicBoardSimpleCommand):

    Syntax        = "PULSE=([0-3]) ([0-9]{1,5})"

    def __init__(self, number, millis):
        super(SetPulseCommand,self).__init__()
        self.number = int(number)
        self.millis = int(millis)

    def __str__(self):
        return "PULSE=%s %s" % (
                self.number,
                self.millis
            )

#Register SetPulseCommand
UdPicBoardSimpleCommand.SUBCLASSES += (SetPulseCommand,)

class AdjustCommand(UdPicBoardSimpleCommand):

    Syntax = "ADJUST=([0-3]) ([0-4].[0-9]|5.0)"

    def __init__(self, number, power):
        super(AdjustCommand,self).__init__()
        self.number   = int(number)
        self.power    = float(power)

    def __str__(self):
        return "ADJUST=%s %s" % (self.number, self.power)

#Register AdjustCommand
UdPicBoardSimpleCommand.SUBCLASSES += (AdjustCommand,)

class WriteCommand(UdPicBoardSimpleCommand):

    Syntax = "WRITE=([0]) (.*) EOT" # EOT = End Of Text

    def __init__(self, number, text):
        super(WriteCommand,self).__init__()
        self.number   = int(number)
        self.text     = text

    def __str__(self):
        return "WRITE=%s %s EOT" % (self.number, self.text)

#Register WriteCommand
UdPicBoardSimpleCommand.SUBCLASSES += (WriteCommand,)

class ResetCommand(UdPicBoardSimpleCommand):

    Syntax = "RESET="

    def __init__(self):
        super(ResetCommand,self).__init__()

    def __str__(self):
        return "RESET="

#Register ChangeSwitchCommand
UdPicBoardSimpleCommand.SUBCLASSES += (ResetCommand,)
