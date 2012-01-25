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

import experiments.ud_xilinx.exc as UdXilinxExperimentExceptions

class UdBoardCommand(object):

    _REGEX_FORMAT="^((%(complete-syntax)s, )*%(complete-syntax)s)$" 
    @staticmethod
    def get_syntax():
        return UdBoardCommand._REGEX_FORMAT % { 
            'complete-syntax' : UdBoardSimpleCommand.get_full_syntax()
        }

    def __init__(self, command):
        mo = re.match(UdBoardCommand.get_syntax(), command)
        if mo == None:
            raise UdXilinxExperimentExceptions.InvalidUdBoardCommandException(
                    "Invalid command format; %s required" % UdBoardCommand.get_syntax()
                )
        self._commands = []
        for i in command.split(', '):
            self._commands.append(UdBoardSimpleCommand.create(i))

    def get_codes(self):
        codes = ()
        for i in self._commands:
            codes += (i.get_code(),)
        return codes

class UdBoardSimpleCommand(object):

    SUBCLASSES = ()

    def __init__(self):
        super(UdBoardSimpleCommand,self).__init__()

    @staticmethod
    def create(str_command):
        for SubClass in UdBoardSimpleCommand.SUBCLASSES:
            mo = re.match(SubClass.Syntax, str_command)
            if mo != None:
                return SubClass(*(mo.groups()))

    @staticmethod
    def get_full_syntax():
        syntax = '('
        for i in UdBoardSimpleCommand.SUBCLASSES:
            syntax += '%s|' % i.Syntax
        return syntax[:-1] + ')'

def on_off_to_bool(on_off):
    if on_off == "on":
        return True
    elif on_off == "off":
        return False
    else:
        raise UdXilinxExperimentExceptions.IllegalStatusUdBoardCommandException("%s is not on nor off" % on_off)

def bool_to_on_off(on_off):
    if on_off:
        return "on"
    else:
        return "off"

#####################################################
######    UdBoardSimpleCommand Implementors   #######
#####################################################

class ChangeSwitchCommand(UdBoardSimpleCommand):

    Syntax = "ChangeSwitch (on|off) ([0-9])"

    def __init__(self, switch_on, number):
        super(ChangeSwitchCommand,self).__init__()
        self.switch_on = on_off_to_bool(switch_on)
        self.number = int(number)

    def get_code(self):
        num = (self.number + 1) * 2
        if self.switch_on:
            num -= 1
        return num

    def __str__(self):
        return "ChangeSwitch %s %s" % (
                bool_to_on_off(self.switch_on), 
                self.number
            )

#Register ChangeSwitchCommand
UdBoardSimpleCommand.SUBCLASSES += (ChangeSwitchCommand,)

class SetPulseCommand(UdBoardSimpleCommand):

    Syntax        = "SetPulse (on|off) ([0-3])"

    def __init__(self, switch_on, number):
        super(SetPulseCommand,self).__init__()
        self.switch_on = on_off_to_bool(switch_on)
        self.number = int(number)

    def get_code(self):
        num = self.number * 2
        if self.switch_on:
            num += 21
        else:
            num += 22
        return num

    def __str__(self):
        return "SetPulse %s %s" % (
                bool_to_on_off(self.switch_on),
                self.number
            )

#Register SetPulseCommand
UdBoardSimpleCommand.SUBCLASSES += (SetPulseCommand,)

class ClockActivationCommand(UdBoardSimpleCommand):

    Syntax = "ClockActivation on (250|500|1000|1500|2000)"

    _frequences =[250,500,1000,1500,2000]

    def __init__(self, freq):
        super(ClockActivationCommand,self).__init__()
        self.freq     = int(freq)

    def get_code(self):
        num = ClockActivationCommand._frequences.index(self.freq)
        num += 32
        return num

    def __str__(self):
        return "ClockActivation on %s" % self.freq

#Register ClockActivationCommand
UdBoardSimpleCommand.SUBCLASSES += (ClockActivationCommand,)

class ClockDeactivationCommand(UdBoardSimpleCommand):

    Syntax = "ClockActivation off"

    def __init__(self):
        super(ClockDeactivationCommand,self).__init__()

    def get_code(self):
        return 37

    def __str__(self):
        return "ClockActivation off"

#Register ClockActivationCommand
UdBoardSimpleCommand.SUBCLASSES += (ClockDeactivationCommand,)

class CleanCommand(UdBoardSimpleCommand):

    Syntax = "CleanInputs"

    def __init__(self):
        super(CleanCommand,self).__init__()

    def get_code(self):
        return 0 # Not implemented in PIC

    def __str__(self):
        return "CleanInputs"

#Register ClockActivationCommand
UdBoardSimpleCommand.SUBCLASSES += (CleanCommand,)

