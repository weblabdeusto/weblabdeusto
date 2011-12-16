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

import weblab.data.command as Command

class ExperimentId(object):
    def __init__(self, exp_name, cat_name):
        self.exp_name  = exp_name
        self.cat_name  = cat_name

    def __eq__(self, other):
        return ( isinstance(other, ExperimentId) 
                and self.exp_name  == other.exp_name
                and self.cat_name  == other.cat_name
            )
    
    def __cmp__(self, other):
        if isinstance(other, ExperimentId):
            return -1
        elif self.exp_name != other.exp_name:
            return cmp(self.exp_name, other.exp_name)
        else:
            return cmp(self.cat_name, other.cat_name)

    def __repr__(self):
        return "ExperimentId( exp_name=%r, cat_name=%r )" % ( self.exp_name, self.cat_name )
    
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
    def __init__(self, inst_name, exp_name, cat_name):
        self.inst_name = inst_name
        self.exp_name  = exp_name
        self.cat_name  = cat_name

    def to_experiment_id(self):
        return ExperimentId(self.exp_name, self.cat_name)

    def to_weblab_str(self):
        return "%s:%s@%s" % (self.inst_name, self.exp_name, self.cat_name)

    def __eq__(self, other):
        return ( isinstance(other, ExperimentInstanceId) 
                and self.inst_name == other.inst_name
                and self.exp_name  == other.exp_name
                and self.cat_name  == other.cat_name
            )

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __hash__(self):
        return hash(self.inst_name) * 31 ** 3 + hash(self.exp_name) * 31 ** 2 + hash(self.cat_name) * 31 + hash("ExperimentInstanceId")

    def __repr__(self):
        return "ExperimentInstanceId(inst_name=%r, exp_name=%r, cat_name=%r )" % ( str(self.inst_name), str(self.exp_name), str(self.cat_name) )


class CommandSent(object):
    def __init__(self, command, timestamp_before, response = None, timestamp_after = None):
        self.command          = command          # Command
        self.timestamp_before = timestamp_before # seconds.millis since 1970 in GMT
        if response == None:
            self.response = Command.NullCommand()
        else:
            self.response = response
        self.timestamp_after = timestamp_after

    def __repr__(self):
        return u'CommandSent(command = %r, timestamp_before = %r, response = %r, timestamp_after = %r)' % (
                        self.command, self.timestamp_before, self.response, self.timestamp_after,)

class FileSent(object):
    def __init__(self, file_sent, file_hash, timestamp_before, response = None, timestamp_after = None, file_info = None):
        self.file_sent        = file_sent
        self.file_hash        = file_hash
        self.file_info        = file_info
        self.timestamp_before = timestamp_before
        if response == None:
            self.response = Command.NullCommand()
        else:
            self.response = response
        self.timestamp_after  = timestamp_after

    def __repr__(self):
        return u'FileSent(file_sent = %r, file_hash = %r, timestamp_before = %r, response = %r, timestamp_after = %r, file_info = %r)' % (
                     self.file_sent, self.file_hash, self.timestamp_before, self.response, self.timestamp_after, self.file_info )

class ExperimentUsage(object):
    def __init__(self, experiment_use_id = None, start_date = None, end_date = None, from_ip = u"unknown", experiment_id = None, reservation_id = None, coord_address = None, commands = None, sent_files = None):
        self.experiment_use_id      = experiment_use_id # int
        self.start_date             = start_date        # seconds.millis since 1970 in GMT
        self.end_date               = end_date          # seconds.millis since 1970 in GMT
        self.from_ip                = from_ip 
        self.experiment_id          = experiment_id     # weblab.data.experiments.ExperimentId
        self.reservation_id         = reservation_id    # string, the reservation identifier
        self.coord_address          = coord_address     # voodoo.gen.coordinator.CoordAddress.CoordAddress

        if commands is None:
            self.commands           = []   # [CommandSent]
        else:
            self.commands           = commands

        if sent_files is None:
            self.sent_files         = []   # [FileSent]
        else:
            self.sent_files         = sent_files

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

    def update_command(self, command_id, command_sent):
        # isinstance(command_sent, CommandSent)
        self.commands[command_id] = command_sent

    def append_file(self, file_sent):
        # isinstance(file_sent, FileSent)
        self.sent_files.append(file_sent)
        return len(self.sent_files) - 1

    def update_file(self, file_id, file_sent):
        # isinstance(file_sent, FileSent)
        self.sent_files[file_id] = file_sent

    def __repr__(self):
        return   u"""ExperimentUsage(experiment_use_id = %r, start_date = %r, end_date = %r, from_ip = %r, experiment_id = %r, reservation_id = %r, coord_address = %r, commands = %r, sent_files = %r)""" % (
                                self.experiment_use_id, self.start_date, self.end_date, self.from_ip, self.experiment_id, self.reservation_id, self.coord_address, self.commands, self.sent_files )

