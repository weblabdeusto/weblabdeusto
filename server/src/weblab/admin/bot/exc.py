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
from __future__ import print_function, unicode_literals

class BotError(Exception):
    """ Base Exception for this tool. """

    def __init__(self, *args, **kargs):
        Exception.__init__(self, *args, **kargs)

class InvalidUserOrPasswordError(BotError):
    def __init__(self, *args, **kargs):
        BotError.__init__(self, *args, **kargs)

class ListOfExperimentsIsEmptyError(BotError):
    def __init__(self, *args, **kargs):
        BotError.__init__(self, *args, **kargs)

class ExperimentDoesNotExistError(BotError):
    def __init__(self, *args, **kargs):
        BotError.__init__(self, *args, **kargs)

class UserAssertionError(BotError):
    def __init__(self, *args, **kargs):
        BotError.__init__(self, *args, **kargs)

