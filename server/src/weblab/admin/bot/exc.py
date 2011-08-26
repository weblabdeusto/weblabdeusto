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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

class BotException(Exception):
    """ Base Exception for this tool. """
    
    def __init__(self, *args, **kargs):
        Exception.__init__(self, *args, **kargs)
        
class InvalidUserOrPasswordException(BotException):
    def __init__(self, *args, **kargs):
        BotException.__init__(self, *args, **kargs)
        
class ListOfExperimentsIsEmptyException(BotException):
    def __init__(self, *args, **kargs):
        BotException.__init__(self, *args, **kargs)
        
class ExperimentDoesNotExistException(BotException):
    def __init__(self, *args, **kargs):
        BotException.__init__(self, *args, **kargs)

class UserAssertionException(BotException):
    def __init__(self, *args, **kargs):
        BotException.__init__(self, *args, **kargs)
        
