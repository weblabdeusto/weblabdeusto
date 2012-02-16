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

import base64
import os
import weblab.data.command as Command

from voodoo.override import Override
from voodoo.gen.coordinator.CoordAddress import CoordAddress
from voodoo.representable import AbstractRepresentable, Representable
from voodoo.typechecker import typecheck

class ExperimentId(object):

    __metaclass__ = Representable

    @typecheck(basestring, basestring)
    def __init__(self, exp_name, cat_name):
        self.exp_name  = unicode(exp_name)
        self.cat_name  = unicode(cat_name)

    def __cmp__(self, other):
        if isinstance(other, ExperimentId):
            return -1
        if self.exp_name != other.exp_name:
            return cmp(self.exp_name, other.exp_name)

        return cmp(self.cat_name, other.cat_name)

    def to_dict(self):
        return {'exp_name': self.exp_name, 'cat_name': self.cat_name}

    def to_weblab_str(self):
        return '%s@%s' % (self.exp_name, self.cat_name)

    @staticmethod
    def parse(weblab_str):
        pos = weblab_str.find("@")
        experiment_name = weblab_str[:pos]
        category_name   = weblab_str[pos + 1 :]
        return ExperimentId(experiment_name, category_name)

class ExperimentInstanceId(object):

    __metaclass__ = Representable

    @typecheck(basestring, basestring, basestring)
    def __init__(self, inst_name, exp_name, cat_name):
        self.inst_name = unicode(inst_name)
        self.exp_name  = unicode(exp_name)
        self.cat_name  = unicode(cat_name)

    def to_experiment_id(self):
        return ExperimentId(self.exp_name, self.cat_name)

    def to_weblab_str(self):
        return "%s:%s@%s" % (self.inst_name, self.exp_name, self.cat_name)

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __hash__(self):
        return hash(self.inst_name) * 31 ** 3 + hash(self.exp_name) * 31 ** 2 + hash(self.cat_name) * 31 + hash("ExperimentInstanceId")

class CommandSent(object):

    __metaclass__ = Representable

    @typecheck(Command.Command, float, Command.Command, (float, type(None)))
    def __init__(self, command, timestamp_before, response = None, timestamp_after = None):
        self.command          = command          # Command
        self.timestamp_before = timestamp_before # seconds.millis since 1970 in GMT
        if response == None:
            self.response = Command.NullCommand()
        else:
            self.response = response
        self.timestamp_after = timestamp_after

class LoadedFileSent(object):

    __metaclass__ = Representable

    @typecheck(basestring, float, Command.Command, (float, type(None)), (basestring, type(None)))
    def __init__(self, file_content, timestamp_before, response, timestamp_after, file_info):
        self.file_content     = file_content
        self.timestamp_before = timestamp_before
        self.response         = response
        self.timestamp_after  = timestamp_after
        self.file_info        = file_info

    # Just in case
    def load(self):
        return self

class FileSent(object):

    __metaclass__ = Representable

    @typecheck(basestring, basestring, float, Command.Command, (float, type(None)), (basestring, type(None)))
    def __init__(self, file_path, file_hash, timestamp_before, response = None, timestamp_after = None, file_info = None):
        self.file_path        = file_path
        self.file_hash        = file_hash
        self.file_info        = file_info
        self.timestamp_before = timestamp_before
        if response == None:
            self.response = Command.NullCommand()
        else:
            self.response = response
        self.timestamp_after  = timestamp_after

    @typecheck(basestring)
    def load(self, storage_path):
        content = base64.encodestring(open(os.sep.join((storage_path, self.file_path)), 'rb').read())
        return LoadedFileSent(content, self.timestamp_before, self.response, self.timestamp_after, self.file_info)

class ExperimentUsage(object):

    __metaclass__ = Representable

    @typecheck(int, float, float, basestring, ExperimentId, basestring, CoordAddress, dict, list, list)
    def __init__(self, experiment_use_id = None, start_date = None, end_date = None, from_ip = u"unknown", experiment_id = None, reservation_id = None, coord_address = None, request_info = None, commands = None, sent_files = None):
        self.experiment_use_id      = experiment_use_id # int
        self.start_date             = start_date        # seconds.millis since 1970 in GMT
        self.end_date               = end_date          # seconds.millis since 1970 in GMT
        self.from_ip                = from_ip
        self.experiment_id          = experiment_id     # weblab.data.experiments.ExperimentId
        self.reservation_id         = reservation_id    # string, the reservation identifier
        self.coord_address          = coord_address     # voodoo.gen.coordinator.CoordAddress.CoordAddress
        if request_info is None:
            self.request_info       = {}
        else:
            self.request_info       = request_info

        if commands is None:
            self.commands           = []   # [CommandSent]
        else:
            self.commands           = commands

        if sent_files is None:
            self.sent_files         = []   # [FileSent]
        else:
            self.sent_files         = sent_files

    @typecheck(CommandSent)
    def append_command(self, command_sent):
        """
        append_command(command_sent)
        Appends the specified command to the local list of commands,
        so that later the commands that were sent during the session
        can be retrieved for logging or other purposes.

        @param command_sent The command that was just sent, which we will register
        @return The index of the command we just added in the internal list. Mostly,
        for identification purposes.
        """
        # isinstance(command_sent, CommandSent)
        self.commands.append(command_sent)
        return len(self.commands) - 1

    @typecheck(int, CommandSent)
    def update_command(self, command_id, command_sent):
        self.commands[command_id] = command_sent

    @typecheck((FileSent, LoadedFileSent))
    def append_file(self, file_sent):
        self.sent_files.append(file_sent)
        return len(self.sent_files) - 1

    @typecheck(int, FileSent)
    def update_file(self, file_id, file_sent):
        self.sent_files[file_id] = file_sent

    @typecheck(basestring)
    def load_files(self, path):
        loaded_sent_files = []
        for sent_file in self.sent_files:
            loaded_sent_file = sent_file.load(path)
            loaded_sent_files.append(loaded_sent_file)
        self.sent_files = loaded_sent_files
        return self

class ReservationResult(object):

    __metaclass__ = AbstractRepresentable

    ALIVE     = 'alive'
    CANCELLED = 'cancelled'
    FINISHED  = 'finished'
    FORBIDDEN = 'forbidden'

    def __init__(self, status):
        self.status = status

    def is_alive(self):
        return False

    def is_finished(self):
        return False

    def is_cancelled(self):
        return False

    def is_forbidden(self):
        return False

class AliveReservationResult(ReservationResult):

    def __init__(self, running):
        super(AliveReservationResult, self).__init__(ReservationResult.ALIVE)
        self.running = running
        self.waiting = not running

    @Override(ReservationResult)
    def is_alive(self):
        return True

class RunningReservationResult(AliveReservationResult):

    def __init__(self):
        super(RunningReservationResult, self).__init__(True)

class WaitingReservationResult(AliveReservationResult):

    def __init__(self):
        super(WaitingReservationResult, self).__init__(True)

class CancelledReservationResult(ReservationResult):

    def __init__(self):
        super(CancelledReservationResult, self).__init__(ReservationResult.CANCELLED)

    @Override(ReservationResult)
    def is_cancelled(self):
        return True

class ForbiddenReservationResult(ReservationResult):

    def __init__(self):
        super(ForbiddenReservationResult, self).__init__(ReservationResult.FORBIDDEN)

    @Override(ReservationResult)
    def is_forbidden(self):
        return True

class FinishedReservationResult(ReservationResult):

    @typecheck(ExperimentUsage)
    def __init__(self, experiment_use):
        super(FinishedReservationResult, self).__init__(ReservationResult.FINISHED)
        self.experiment_use = experiment_use

    @Override(ReservationResult)
    def is_finished(self):
        return True

