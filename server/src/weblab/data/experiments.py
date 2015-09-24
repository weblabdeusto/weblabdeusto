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

import base64
import os
import traceback
import StringIO
import weblab.data.command as Command

from voodoo.override import Override
from voodoo.gen import CoordAddress
from voodoo.representable import AbstractRepresentable, Representable
from voodoo.typechecker import typecheck

from weblab.core.file_storer import FileStorer

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

    def __hash__(self):
        return hash(self.to_weblab_str())

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

    @staticmethod
    def parse(weblab_str):
        if ':' not in weblab_str:
            raise ValueError("Malformed weblab_str: ':' not found: %r" % weblab_str)
        pos = weblab_str.find(":")
        instance_name     = weblab_str[:pos]
        experiment_id_str = weblab_str[pos + 1 :]
        experiment_id     = ExperimentId.parse(experiment_id_str)
        return ExperimentInstanceId(instance_name, experiment_id.exp_name, experiment_id.cat_name)

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
    def load(self, storage_path):
        return self

    def is_loaded(self):
        return True

    @typecheck(basestring)
    def save(self, cfg_manager, reservation_id):
        content = base64.decodestring(self.file_content)

        storer = FileStorer(cfg_manager, reservation_id)
        file_stored = storer.store_file(content, self.file_info)
        file_path = file_stored.file_path
        file_hash = file_stored.file_hash
        return FileSent(file_path, file_hash, self.timestamp_before, self.response, self.timestamp_after, self.file_info)

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

    def is_loaded(self):
        return False

    @typecheck(basestring)
    def load(self, storage_path):
        try:
            content = open(os.path.join(storage_path, self.file_path), 'rb').read()
        except:
            sio = StringIO.StringIO()
            traceback.print_exc(file=sio)
            content = "ERROR:File could not be retrieved. Reason: %s" % sio.getvalue()

        content_serialized = base64.encodestring(content)
        return LoadedFileSent(content_serialized, self.timestamp_before, self.response, self.timestamp_after, self.file_info)

    # Just in case
    @typecheck(basestring)
    def save(self, cfg_manager, reservation_id):
        return self

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
        self.coord_address          = coord_address     # voodoo.gen.CoordAddress
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

    @typecheck(basestring)
    def save_files(self, cfg_manager):
        saved_sent_files = []
        for sent_file in self.sent_files:
            saved_sent_file = sent_file.save(cfg_manager, self.reservation_id)
            saved_sent_files.append(saved_sent_file)
        self.sent_files = saved_sent_files
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

