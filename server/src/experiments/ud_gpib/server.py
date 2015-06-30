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

import weblab.experiment.experiment as Experiment
import weblab.experiment.devices.gpib.gpib as Gpib

from voodoo.gen.caller_checker import caller_check
import weblab.experiment.util as ExperimentUtil
import weblab.experiment.exc as ExperimentErrors
import experiments.ud_gpib.exc as GpibErrors
import weblab.data.server_type as ServerType

from voodoo.override import Override
from voodoo.log import logged
import voodoo.log as log
import tempfile
import os

#TODO: which exceptions should the user see and which ones should not?
class UdGpibExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdGpibExperiment,self).__init__(*args, **kwargs)

        self._cfg_manager   = cfg_manager
        self._gpib_compiler = self._create_gpib_compiler(cfg_manager)
        self._gpib_launcher = self._create_gpib_launcher(cfg_manager)
        self.exec_basename  = ''

    def _create_gpib_compiler(self, cfg_manager):
        # For testing purposes
        return Gpib.Compiler(cfg_manager)
    
    def _create_gpib_launcher(self, cfg_manager):
        # For testing purposes
        return Gpib.Launcher(cfg_manager)
    
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_get_api(self):
        return "1"

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info",except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        try:
            file_content_recovered = self._extract_content(file_content)
            src_file_name = self._write_content_to_file(file_content_recovered)
            src_basename = src_file_name.split(os.sep)[-1]

            log.log(
                UdGpibExperiment,
                log.level.Info,
                "Compiling file"
            )
            exe_file_name = self._compile(src_basename)
            self.exec_basename = exe_file_name.split(os.sep)[-1]

            log.log(
                UdGpibExperiment,
                log.level.Info,
                "Executing file"
            )
            if self._cfg_manager.get_value('gpib_just_testing', False):
                self.exec_basename = "." + os.sep + self.exec_basename
            self._execute(self.exec_basename, True)
            

        except Exception as e:
            log.log(
                UdGpibExperiment,
                log.level.Info,
                "Exception joining sending program to device: %s" % e.args[0]
            )
            log.log_exc(
                UdGpibExperiment,
                log.level.Info
            )
            raise ExperimentErrors.SendingFileFailureError(
                    "Error sending file to device: %s" % str(e.args)
                )

    @Override(Experiment.Experiment)
    @logged("info")
    @caller_check(ServerType.Laboratory)
    def do_dispose(self):
#       try:
#           os.remove(self._cfg_manager.get_value('gpib_public_output_file_filename'))
#       except:
#           pass
        pass

    # Kludge: Converting outputs to ascii so as to avoid encoding problems
    def _remove_non_ascii_characters(self, text):
        text = text.replace("�","a")
        text = text.replace("�","e")
        text = text.replace("�","i")
        text = text.replace("�","o")
        text = text.replace("�","u")
        text = text.replace("�","A")
        text = text.replace("�","E")
        text = text.replace("�","I")
        text = text.replace("�","O")
        text = text.replace("�","U")
        text = text.replace("�","ny")
        text = text.replace("�","NY")
        for i in xrange(len(text)):
            if ord(text[i]) >= 128:
                text = text.replace(text[i], " ")
        return text

    def _extract_content(self, initial_content):
        #TODO: encode? utf8?
        if isinstance(initial_content, unicode):
            file_content_encoded = initial_content.encode('utf8')
        else:
            file_content_encoded = initial_content
        file_content_recovered = ExperimentUtil.deserialize(file_content_encoded)
        return file_content_recovered

    def _write_content_to_file(self, content):
        fd, file_name = tempfile.mkstemp(
                prefix='ud_gpib_experiment_program',
                suffix='.cpp',
                dir='.'
            )
        try:
            os.write(fd, content)
        finally:
            os.close(fd)
        return file_name

    def _compile(self, src_file_name):
        try:
            return self._gpib_compiler.compile_file(src_file_name)
        finally:
            os.remove(src_file_name)

    def _execute(self, exe_file_name, background):
        try:
            self._gpib_launcher.execute(exe_file_name, background)
        finally:
            if not background:
                self._remove_file()
            
    def _read_output_file(self):
        file_filename = self._cfg_manager.get_value('gpib_public_output_file_filename')
        file_content = open(file_filename).read()
#       try:
#           os.remove(file_filename)
#       except:
#           pass
        return file_content
    
    def _remove_file(self):
        try:
            os.remove(self.exec_basename)
        except OSError:
            pass        
    
    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        
        if command == "POLL":
            if self._gpib_launcher.poll():
                log.log(
                    UdGpibExperiment,
                    log.level.Info,
                    "Executed, saving results"
                )
                self._remove_file()
                return "OK"
            else:
                return "WAIT"
        
        elif command == "RESULT code":
            return self._gpib_launcher.get_result_code()

        elif command == "RESULT stdout":
            return self._remove_non_ascii_characters(self._gpib_launcher.get_result_stdout())

        elif command == "RESULT stderr":
            return self._remove_non_ascii_characters(self._gpib_launcher.get_result_stderr())
        
        elif command == "RESULT file":
            try:
                return "OK%s" % self._remove_non_ascii_characters(self._read_output_file())
            except Exception:
                return "ERFile <%s> not found"  % self._cfg_manager.get_value('gpib_public_output_file_filename')
                
        else:
            raise GpibErrors.UnknownUdGpibCommandError("Unknown received command: %s" % command)
