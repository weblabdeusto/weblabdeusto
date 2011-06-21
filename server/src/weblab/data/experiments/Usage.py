#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import weblab.data.Command as Command

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
        return u'<CommandSent before="%s" after="%s"><Command>%s</Command><Response>%s</Response></CommandSent>' % (
                self.timestamp_before,
                self.timestamp_after,
                self.command,
                self.response
            )

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
        return u'<FileSent start="%s" end="%s" info="%s"><file_sent>%s</file_sent><file_hash>%s</file_hash><response>%s</response></FileSent>' % (
                self.timestamp_before,
                self.timestamp_after,
                self.file_info,
                self.file_sent,
                self.file_hash,
                self.response
            )

class ExperimentUsage(object):
    def __init__(self):
        self.experiment_use_id      = None # int
        self.start_date             = None # seconds.millis since 1970 in GMT
        self.end_date               = None # seconds.millis since 1970 in GMT
        self.from_ip                = u"unknown"
        self.experiment_id          = None # weblab.data.experiments.ExperimentId.ExperimentId
        self.coord_address          = None # voodoo.gen.coordinator.CoordAddress.CoordAddress
        self.commands               = []   # [CommandSent]
        self.sent_files             = []   # [FileSent]

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
        usages = u"""<ExperimentUsage usage_id="%s" start_date="%s" end_date="%s" from_ip="%s" to="%s"><experiment_id>%s</experiment_id><commands>""" % (
                self.experiment_use_id,
                self.start_date,
                self.end_date,
                self.coord_address,
                self.from_ip,
                self.experiment_id,
            )
        for command in self.commands:
            usages += unicode(command)
        usages += u'</commands><sent_files>'
        for sent_file in self.sent_files:
            usages += unicode(sent_file)
        return usages + u'</sent_files></ExperimentUsage>'

