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
from __future__ import print_function, unicode_literals

from voodoo.representable import Representable
from voodoo.typechecker import typecheck

class Command(object):

    __metaclass__ = Representable

    @typecheck((basestring, typecheck.NONE))
    def __init__(self, commandstring):
        self.commandstring = commandstring

    def get_command_string(self):
        return self.commandstring

    def __cmp__(self, other):
        if isinstance(other, Command):
            return cmp(self.commandstring, other.commandstring)
        return -1

    def to_dict(self):
        return {'commandstring': self.commandstring}

class NullCommand(Command):

    def __init__(self):
        super(NullCommand, self).__init__(None)

